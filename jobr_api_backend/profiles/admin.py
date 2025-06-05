from django.contrib import admin
from .models import Education, WorkExperience, PortfolioItem

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('institution', 'degree', 'field_of_study', 'is_ongoing', 'employee', 'grade')
    list_filter = ('is_ongoing', 'degree', 'field_of_study')
    search_fields = ('institution', 'degree', 'field_of_study', 'employee__user__username', 'description')
    raw_id_fields = ('employee',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'position', 'start_date', 'end_date', 'is_current_position', 'employee', 'location')
    list_filter = ('is_current_position', 'start_date', 'end_date', 'location')
    search_fields = ('company_name', 'position', 'location', 'employee__user__username', 'description')
    ordering = ('-start_date',)
    raw_id_fields = ('employee',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    list_per_page = 25

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_public', 'view_count', 'like_count', 'employee', 'client_rating')
    list_filter = ('is_public', 'date', 'client_rating', 'created_at')
    search_fields = ('title', 'description', '_tags', 'employee__user__username', 'client_name')
    ordering = ('-date',)
    raw_id_fields = ('employee',)
    readonly_fields = ('view_count', 'like_count', 'created_at', 'updated_at')
    date_hierarchy = 'date'
    list_per_page = 25

    def get_queryset(self, request):
        """
        Add annotation for array length of tags.
        """
        qs = super().get_queryset(request)
        return qs.prefetch_related('employee__user')
