from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .models import Review, CustomUser, Employee, Employer, UserGallery

# Unregister unwanted models from admin
admin.site.unregister(Group)
admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined', 'last_login')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_per_page = 25
    date_hierarchy = 'date_joined'

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'gender', 'city_name', 'phone_number', 'date_of_birth')
    list_filter = ('gender', 'city_name', 'language', 'contract_type', 'function')
    search_fields = ('city_name', 'biography')
    list_per_page = 25

    def get_username(self, obj):
        return str(obj)
    get_username.short_description = 'Username'

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'company_name', 'city', 'postal_code', 'website')
    list_filter = ('city', 'postal_code')
    search_fields = ('company_name', 'vat_number', 'city', 'biography')
    list_per_page = 25

    def get_username(self, obj):
        return str(obj)
    get_username.short_description = 'Username'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('get_reviewer', 'rating', 'reviewer_type', 'created_at')
    list_filter = ('rating', 'reviewer_type', 'created_at')
    search_fields = ('comment', 'anonymous_name')
    date_hierarchy = 'created_at'
    list_per_page = 25

    def get_reviewer(self, obj):
        if obj.reviewer_type == 'employee' and obj.employee:
            return f"Employee: {obj.employee}"
        elif obj.reviewer_type == 'employer' and obj.employer:
            return f"Employer: {obj.employer}"
        return f"Anonymous: {obj.anonymous_name or 'Unknown'}"
    get_reviewer.short_description = 'Reviewer'

@admin.register(UserGallery)
class UserGalleryAdmin(admin.ModelAdmin):
    list_display = ('user', 'gallery')
    list_filter = ('user',)
    search_fields = ('user__username', 'user__email')
    list_per_page = 25
