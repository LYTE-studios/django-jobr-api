from django.contrib import admin
from .models import Education, WorkExperience, PortfolioItem

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_ongoing', 'employee')
    list_filter = ('is_ongoing', 'degree')
    search_fields = ('institution', 'degree', 'field_of_study', 'employee__user__username')
    ordering = ('-start_date',)
    raw_id_fields = ('employee',)

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'position', 'start_date', 'end_date', 'is_current_position', 'employment_type', 'employee')
    list_filter = ('is_current_position', 'employment_type')
    search_fields = ('company_name', 'position', 'location', 'employee__user__username')
    ordering = ('-start_date',)
    raw_id_fields = ('employee',)

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_public', 'view_count', 'like_count', 'employee')
    list_filter = ('is_public', 'date')
    search_fields = ('title', 'description', 'tags', 'employee__user__username')
    ordering = ('-date',)
    raw_id_fields = ('employee',)
    readonly_fields = ('view_count', 'like_count')

    def get_queryset(self, request):
        """
        Add annotation for array length of tags.
        """
        qs = super().get_queryset(request)
        return qs.prefetch_related('employee__user')
