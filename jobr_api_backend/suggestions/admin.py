from django.contrib import admin
from .models import AISuggestion, SuggestionWeight


@admin.register(AISuggestion)
class AISuggestionAdmin(admin.ModelAdmin):
    list_display = [
        'employee',
        'vacancy',
        'quantitative_score',
        'qualitative_score',
        'total_score',
        'created_at',
    ]
    list_filter = [
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'employee__user__email',
        'vacancy__title',
        'message',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
    ]


@admin.register(SuggestionWeight)
class SuggestionWeightAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'weight',
        'mastery_level',
        'field_type',
    ]
    list_filter = [
        'mastery_level',
        'field_type',
    ]
    search_fields = [
        'name',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
