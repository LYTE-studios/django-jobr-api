from django.contrib import admin
from .models import (
    Vacancy, Question, ContractType, Function, Language, Skill, Location,
    SalaryBenefit, ProfileInterest, JobListingPrompt, VacancyLanguage,
    VacancyDescription, VacancyQuestion, ApplyVacancy, Weekday, Sector,
    FunctionSkill
)

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('location', 'weight')
    search_fields = ('location',)
    list_filter = ('weight',)
    ordering = ('location',)
    list_per_page = 25

@admin.register(ContractType)
class ContractTypeAdmin(admin.ModelAdmin):
    list_display = ('contract_type', 'weight')
    search_fields = ('contract_type',)
    list_filter = ('weight',)
    ordering = ('contract_type',)
    list_per_page = 25

class FunctionSkillInline(admin.TabularInline):
    model = FunctionSkill
    extra = 1
    autocomplete_fields = ['skill']
    ordering = ['-weight']

@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ('function', 'weight', 'sector', 'get_skills_count')
    search_fields = ('function', 'sector__name')
    list_filter = ('weight', 'sector')
    ordering = ('function',)
    list_per_page = 25
    inlines = [FunctionSkillInline]

    def get_skills_count(self, obj):
        return obj.skills.count()
    get_skills_count.short_description = 'Skills'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'weight')
    search_fields = ('question',)
    list_filter = ('weight',)
    ordering = ('question',)
    list_per_page = 25

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('language', 'weight')
    search_fields = ('language',)
    list_filter = ('weight',)
    ordering = ('language',)
    list_per_page = 25

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('skill', 'category', 'get_functions_count')
    search_fields = ('skill',)
    list_filter = ('category',)
    ordering = ('skill',)
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

@admin.register(VacancyLanguage)
class VacancyLanguageAdmin(admin.ModelAdmin):
    list_display = ('language', 'mastery')
    list_filter = ('mastery', 'language')
    search_fields = ('language__language',)
    list_per_page = 25

@admin.register(VacancyDescription)
class VacancyDescriptionAdmin(admin.ModelAdmin):
    list_display = ('get_description_preview', 'question')
    list_filter = ('question',)
    search_fields = ('description',)
    list_per_page = 25

    def get_description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    get_description_preview.short_description = 'Description'

@admin.register(VacancyQuestion)
class VacancyQuestionAdmin(admin.ModelAdmin):
    list_display = ('question',)
    search_fields = ('question',)
    list_per_page = 25

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('get_employer', 'function', 'location', 'job_date', 'salary', 'expected_mastery')
    list_filter = (
        'expected_mastery',
        'contract_type',
        'location',
        'function',
        'week_day',
        'job_date',
    )
    search_fields = (
        'employer__username',
        'employer__email',
        'function__function',
        'location__location',
    )
    filter_horizontal = ('contract_type', 'week_day', 'languages', 'descriptions', 'questions', 'skill')
    raw_id_fields = ('employer',)
    date_hierarchy = 'job_date'
    list_per_page = 25

    def get_employer(self, obj):
        return obj.employer.username
    get_employer.short_description = 'Employer'

@admin.register(ApplyVacancy)
class ApplyVacancyAdmin(admin.ModelAdmin):
    list_display = ('employee', 'vacancy')
    list_filter = ('employee', 'vacancy')
    search_fields = ('employee__username', 'vacancy__employer__username')
    raw_id_fields = ('employee', 'vacancy')
    list_per_page = 25