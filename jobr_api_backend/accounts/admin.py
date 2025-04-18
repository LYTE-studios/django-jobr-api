from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .models import (
    CustomUser, Employee, Admin, ProfileOption,
    Review, Company, CompanyUser
)

# Unregister unwanted models from admin
admin.site.unregister(Group)
admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)

class OneToOneInline(admin.StackedInline):
    template = 'admin/edit_inline/stacked.html'
    can_delete = False
    max_num = 1
    min_num = 1

    def has_add_permission(self, request, obj=None):
        return False

class EmployeeInline(OneToOneInline):
    model = Employee
    verbose_name_plural = 'Employee Profile'
    fk_name = 'user'

class CompanyUserInline(admin.TabularInline):
    model = CompanyUser
    extra = 1
    verbose_name = "Company Membership"
    verbose_name_plural = "Company Memberships"

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'vat_number', 'city', 'created_at')
    list_filter = ('city', 'created_at')
    search_fields = ('name', 'vat_number', 'city')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CompanyUserInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'vat_number', 'sector')
        }),
        ('Location', {
            'fields': ('street_name', 'house_number', 'city', 'postal_code')
        }),
        ('Profile Images', {
            'fields': ('profile_picture', 'profile_banner')
        }),
        ('Additional Information', {
            'fields': ('website', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class AdminInline(OneToOneInline):
    model = Admin
    verbose_name_plural = 'Admin Profile'
    fk_name = 'user'

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_blocked', 'date_joined', 'last_login')
    list_filter = ('role', 'is_active', 'is_blocked', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_per_page = 25
    date_hierarchy = 'date_joined'
    actions = ['block_users', 'unblock_users']

    def get_fieldsets(self, request, obj=None):
        if not obj:
            # For creating a new user
            return (
                (None, {'fields': ('username', 'password1', 'password2')}),
                ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'role', 'selected_company')}),
                ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_blocked')}),
            )
        # For editing an existing user
        return (
            (None, {'fields': ('username', 'password')}),
            ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'role', 'selected_company')}),
            ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_blocked')}),
            ('Important dates', {'fields': ('last_login', 'date_joined')}),
        )

    def get_inlines(self, request, obj=None):
        if not obj:  # No inlines when creating a new user
            return []
        
        inlines = []
        # Show profile fields based on role
        if obj.role == ProfileOption.EMPLOYEE:
            inlines.append(EmployeeInline)
        elif obj.role == ProfileOption.EMPLOYER:
            inlines.append(CompanyUserInline)
        elif obj.role == ProfileOption.ADMIN:
            inlines.append(AdminInline)
        return inlines

    def block_users(self, request, queryset):
        queryset.update(is_blocked=True, is_active=False)
        self.message_user(request, f"{queryset.count()} users were successfully blocked.")
    block_users.short_description = "Block selected users"

    def unblock_users(self, request, queryset):
        queryset.update(is_blocked=False, is_active=True)
        self.message_user(request, f"{queryset.count()} users were successfully unblocked.")
    unblock_users.short_description = "Unblock selected users"

    def response_add(self, request, obj, post_url_continue=None):
        """Handle response after adding a new user."""
        from django.db import transaction
        
        with transaction.atomic():
            return super().response_add(request, obj, post_url_continue)

    def save_model(self, request, obj, form, change):
        """Handle saving the model and any special fields."""
        from django.db import transaction

        with transaction.atomic():
            # Handle blocked status
            if change and 'is_blocked' in form.changed_data:
                obj.is_active = not obj.is_blocked

            # Check if role is being changed
            if change and 'role' in form.changed_data:
                try:
                    old_obj = self.model.objects.select_for_update().get(pk=obj.pk)
                    old_role = old_obj.role
                    
                    # Clean up old profile if role is changing
                    if old_role == ProfileOption.EMPLOYEE and hasattr(old_obj, 'employee_profile'):
                        old_obj.employee_profile.delete()
                    elif old_role == ProfileOption.ADMIN and hasattr(old_obj, 'admin_profile'):
                        old_obj.admin_profile.delete()
                    
                    # Reset selected company if changing from employer
                    if old_role == ProfileOption.EMPLOYER:
                        obj.selected_company = None
                except self.model.DoesNotExist:
                    pass

            # Save the user
            super().save_model(request, obj, form, change)

            # Create new profile based on role if needed
            if not change or (change and 'role' in form.changed_data):
                if obj.role == ProfileOption.EMPLOYEE and not hasattr(obj, 'employee_profile'):
                    Employee.objects.create(user=obj)
                elif obj.role == ProfileOption.ADMIN and not hasattr(obj, 'admin_profile'):
                    Admin.objects.create(user=obj)

    def response_change(self, request, obj):
        """Handle response after changing a user."""
        from django.db import transaction
        from django.contrib import messages
        
        with transaction.atomic():
            try:
                # Refresh the object to ensure we have the latest data
                obj.refresh_from_db()
                return super().response_change(request, obj)
            except self.model.DoesNotExist:
                messages.warning(request, 'The user no longer exists.')
                return self.response_post_save_change(request, obj)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewed', 'rating', 'created_at', 'updated_at')
    list_filter = ('rating', 'created_at', 'reviewer__role', 'reviewed__role')
    search_fields = (
        'reviewer__username', 'reviewer__email',
        'reviewed__username', 'reviewed__email',
        'comment'
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'

    def save_model(self, request, obj, form, change):
        if not change:  # Only validate on creation
            obj.clean()  # Run model validation
        super().save_model(request, obj, form, change)
