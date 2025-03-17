from django.contrib import admin
from .models import Extra

@admin.register(Extra)
class ExtraAdmin(admin.ModelAdmin):
    list_display = ('extra', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('extra',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')
