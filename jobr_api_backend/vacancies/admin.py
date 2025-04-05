from django.contrib import admin
from django.http import HttpResponseRedirect, Http404
from django.template.response import TemplateResponse
from django.urls import reverse
from django import forms
from .models import (
    Vacancy, Question, ContractType, Function, Language, Skill, Location,
    SalaryBenefit, ProfileInterest, JobListingPrompt, VacancyLanguage,
    VacancyDescription, VacancyQuestion, ApplyVacancy, Weekday, Sector,
    FunctionSkill
)

class SectorAdminForm(forms.ModelForm):
    functions = forms.ModelMultipleChoiceField(
        queryset=Function.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple('Functions', False),
        label='Select Functions'
    )

    class Meta:
        model = Sector
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['functions'].initial = self.instance.functions.all()

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    form = SectorAdminForm
    list_display = ('name', 'weight', 'enabled', 'get_functions_count')
    search_fields = ('name', 'functions__name')
    list_filter = ('weight', 'enabled')
    ordering = ('name',)
    list_per_page = 25

    def get_functions_count(self, obj):
        return obj.functions.count()
    get_functions_count.short_description = 'Functions'

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(ContractType)
class ContractTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

class FunctionSkillInline(admin.TabularInline):
    model = FunctionSkill
    extra = 1
    autocomplete_fields = ['skill']
    fields = ('skill', 'weight')
    verbose_name = "Skill with Weight"
    verbose_name_plural = "Skills with Weights"

class FunctionAdminForm(forms.ModelForm):
    sectors = forms.ModelMultipleChoiceField(
        queryset=Sector.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple('Sectors', False),
        label='Select Sectors'
    )

    class Meta:
        model = Function
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['sectors'].initial = self.instance.sectors.all()

@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    form = FunctionAdminForm
    inlines = [FunctionSkillInline]
    list_display = ('name', 'weight', 'get_sectors', 'get_skills_count')
    search_fields = ('name', 'sectors__name', 'skills__name')
    list_filter = ('weight', 'sectors')
    ordering = ('name',)
    list_per_page = 25

    def get_sectors(self, obj):
        return ", ".join([sector.name for sector in obj.sectors.all()])
    get_sectors.short_description = 'Sectors'

    def get_skills_count(self, obj):
        return obj.skills.count()
    get_skills_count.short_description = 'Skills'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_functions_count')
    search_fields = ('name',)
    list_filter = ('category',)
    ordering = ('name',)
    list_per_page = 25

    def get_functions_count(self, obj):
        return obj.functions.count()
    get_functions_count.short_description = 'Used in Functions'

@admin.register(Weekday)
class WeekdayAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(SalaryBenefit)
class SalaryBenefitAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(ProfileInterest)
class ProfileInterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(JobListingPrompt)
class JobListingPromptAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'function', 'location', 'job_date', 'salary', 'expected_mastery')
    list_filter = (
        'expected_mastery',
        'contract_type',
        'location',
        'function',
        'week_day',
        'job_date',
    )
    search_fields = (
        'title',
        'description',
        'company__name',
        'created_by__email',
        'function__name',
        'location__name',
    )
    filter_horizontal = ('contract_type', 'week_day', 'languages', 'descriptions', 'questions', 'skill')
    raw_id_fields = ('company', 'created_by')
    date_hierarchy = 'job_date'
    list_per_page = 25