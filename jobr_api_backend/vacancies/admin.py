from django.contrib import admin
from django.http import HttpResponseRedirect, Http404
from django.template.response import TemplateResponse
from django.urls import reverse
from django import forms
from django.db import transaction
from django.contrib import messages
import logging
from .models import (
    Vacancy, Question, ContractType, Function, Language, Skill, Location,
    SalaryBenefit, ProfileInterest, JobListingPrompt, VacancyLanguage,
    VacancyDescription, VacancyQuestion, ApplyVacancy, Weekday, Sector,
    FunctionSkill, VacancyDateTime, ExperienceCompany, ExperienceSchool
)

logger = logging.getLogger(__name__)

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

class SectorAdmin(admin.ModelAdmin):
    form = SectorAdminForm
    list_display = ('name', 'weight', 'enabled', 'get_functions_count')
    search_fields = ('name', 'functions__name')
    list_filter = ('weight', 'enabled')
    ordering = ('name',)
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
                
                if 'functions' in form.cleaned_data:
                    selected_functions = form.cleaned_data['functions']
                    logger.info(f"Setting functions for sector {obj.pk}: {[f.pk for f in selected_functions]}")
                    
                    # Clear and set new functions
                    obj.functions.set(selected_functions)
                    
                    # Verify the changes
                    obj.refresh_from_db()
                    saved_functions = set(obj.functions.values_list('id', flat=True))
                    expected_functions = set(f.id for f in selected_functions)
                    
                    if saved_functions != expected_functions:
                        error_msg = (
                            f"Functions were not saved correctly. "
                            f"Expected: {expected_functions}, "
                            f"Got: {saved_functions}"
                        )
                        messages.error(request, error_msg)
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    logger.info(f"Successfully saved functions for sector {obj.pk}")
                
        except Exception as e:
            logger.error(f"Error saving sector relationships: {str(e)}")
            messages.error(request, f"Error saving sector relationships: {str(e)}")
            raise

    def get_functions_count(self, obj):
        return obj.functions.count()
    get_functions_count.short_description = 'Functions'

class FunctionAdminForm(forms.ModelForm):
    all_skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple('Skills', False),
        label='Select Skills'
    )
    
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
            self.fields['all_skills'].initial = self.instance.skills.all()

class FunctionAdmin(admin.ModelAdmin):
    form = FunctionAdminForm
    list_display = ('name', 'weight', 'get_sectors', 'get_skills_count')
    search_fields = ('name', 'sectors__name', 'skills__name')
    list_filter = ('weight', 'sectors')
    ordering = ('name',)
    list_per_page = 25
    change_form_template = 'admin/vacancies/function/change_form.html'
    change_list_template = 'admin/vacancies/function/change_list.html'

    def save_model(self, request, obj, form, change):
        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
                
                # Handle sectors
                if 'sectors' in form.cleaned_data:
                    selected_sectors = form.cleaned_data['sectors']
                    logger.info(f"Setting sectors for function {obj.pk}: {[s.pk for s in selected_sectors]}")
                    
                    # Clear and set new sectors
                    obj.sectors.set(selected_sectors)
                    
                    # Verify the changes
                    obj.refresh_from_db()
                    saved_sectors = set(obj.sectors.values_list('id', flat=True))
                    expected_sectors = set(s.id for s in selected_sectors)
                    
                    if saved_sectors != expected_sectors:
                        error_msg = (
                            f"Sectors were not saved correctly. "
                            f"Expected: {expected_sectors}, "
                            f"Got: {saved_sectors}"
                        )
                        messages.error(request, error_msg)
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    logger.info(f"Successfully saved sectors for function {obj.pk}")
                
                # Handle skills
                if 'all_skills' in form.cleaned_data:
                    selected_skills = form.cleaned_data['all_skills']
                    logger.info(f"Setting skills for function {obj.pk}: {[s.pk for s in selected_skills]}")
                    
                    # Preserve existing weights
                    existing_weights = {
                        fs.skill_id: fs.weight
                        for fs in FunctionSkill.objects.filter(function=obj)
                    }
                    
                    # Clear existing relationships
                    FunctionSkill.objects.filter(function=obj).delete()
                    
                    # Create new relationships
                    FunctionSkill.objects.bulk_create([
                        FunctionSkill(
                            function=obj,
                            skill=skill,
                            weight=existing_weights.get(skill.id, 1)
                        )
                        for skill in selected_skills
                    ])
                    
                    # Verify the changes
                    obj.refresh_from_db()
                    saved_skills = set(obj.skills.values_list('id', flat=True))
                    expected_skills = set(s.id for s in selected_skills)
                    
                    if saved_skills != expected_skills:
                        error_msg = (
                            f"Skills were not saved correctly. "
                            f"Expected: {expected_skills}, "
                            f"Got: {saved_skills}"
                        )
                        messages.error(request, error_msg)
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    logger.info(f"Successfully saved skills for function {obj.pk}")
                
        except Exception as e:
            logger.error(f"Error saving function relationships: {str(e)}")
            messages.error(request, f"Error saving function relationships: {str(e)}")
            raise

    def get_sectors(self, obj):
        return ", ".join([sector.name for sector in obj.sectors.all()])
    get_sectors.short_description = 'Sectors'

    def get_skills_count(self, obj):
        return obj.skills.count()
    get_skills_count.short_description = 'Skills'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:function_id>/edit-weights/<str:skill_type>/',
                self.admin_site.admin_view(self.edit_weights_view),
                name='edit-function-skill-weights',
            ),
            path(
                'sort-weights/',
                self.admin_site.admin_view(self.sort_weights_view),
                name='sort-function-weights',
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_sort_weights_button'] = True
        return super().changelist_view(request, extra_context)

    def sort_weights_view(self, request):
        if request.method == 'POST':
            try:
                with transaction.atomic():
                    for key, value in request.POST.items():
                        if key.startswith('function_'):
                            function_id = int(key.split('_')[1])
                            weight = int(value)
                            Function.objects.filter(id=function_id).update(weight=weight)
                self.message_user(request, "Function weights updated successfully.")
                return HttpResponseRedirect(reverse('admin:vacancies_function_changelist'))
            except Exception as e:
                self.message_user(request, f"Error updating weights: {str(e)}", level='ERROR')
                
        functions = Function.objects.all().order_by('-weight', 'name')
        context = {
            'title': 'Sort Functions',
            'functions': functions,
            'opts': self.model._meta,
            'media': self.media,
        }
        return TemplateResponse(
            request,
            'admin/vacancies/function/sort_weights.html',
            context,
        )

    def edit_weights_view(self, request, function_id, skill_type=None):
        function = self.get_object(request, function_id)
        
        if not function:
            raise Http404("Function does not exist")

        if skill_type not in ['hard', 'soft']:
            raise Http404("Invalid skill type")

        class SkillWeightForm(forms.Form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                function_skills = FunctionSkill.objects.filter(
                    function=function,
                    skill__category=skill_type
                ).select_related('skill').order_by('weight')
                
                for function_skill in function_skills:
                    self.fields[f'weight_{function_skill.skill.id}'] = forms.IntegerField(
                        label=function_skill.skill.name,
                        initial=function_skill.weight,
                        min_value=0,
                        required=True
                    )

        if request.method == 'POST':
            post_data = {
                f'weight_{key.split("_")[-1]}': value
                for key, value in request.POST.items()
                if key.startswith('weight_')
            }
            
            form = SkillWeightForm(post_data)
            if form.is_valid():
                with transaction.atomic():
                    function_skills = FunctionSkill.objects.filter(
                        function=function,
                        skill__category=skill_type
                    ).select_related('skill')
                    
                    new_weights = {
                        int(key.split('_')[1]): value
                        for key, value in form.cleaned_data.items()
                    }
                    
                    for function_skill in function_skills:
                        if function_skill.skill.id in new_weights:
                            function_skill.weight = new_weights[function_skill.skill.id]
                            function_skill.save()
                
                self.message_user(request, f"{skill_type.title()} skill weights updated successfully.")
                return HttpResponseRedirect(
                    reverse('admin:vacancies_function_change', args=[function.pk])
                )
            else:
                self.message_user(request, "Error updating weights. Please check the values.", level='ERROR')
        else:
            form = SkillWeightForm()

        context = {
            'title': f'Edit {skill_type.title()} Skill Weights for {function}',
            'form': form,
            'opts': self.model._meta,
            'original': function,
            'media': self.media + form.media,
            'skill_type': skill_type,
        }
        return TemplateResponse(
            request,
            'admin/vacancies/function/edit_weights.html',
            context,
        )

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

class ContractTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_functions_count')
    search_fields = ('name',)
    list_filter = ('category',)
    ordering = ('name',)
    list_per_page = 25

    def get_functions_count(self, obj):
        return obj.functions.count()
    get_functions_count.short_description = 'Used in Functions'

class WeekdayAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

class SalaryBenefitAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

class ProfileInterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

class JobListingPromptAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

class VacancyDateTimeInline(admin.TabularInline):
    model = VacancyDateTime
    extra = 1

class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'function', 'location', 'salary', 'expected_mastery')
    list_filter = (
        'expected_mastery',
        'contract_type',
        'location',
        'function',
        'week_day',
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
    inlines = [VacancyDateTimeInline]
    list_per_page = 25

# Register all models
admin.site.register(Sector, SectorAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(ContractType, ContractTypeAdmin)
admin.site.register(Function, FunctionAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Weekday, WeekdayAdmin)
admin.site.register(SalaryBenefit, SalaryBenefitAdmin)
admin.site.register(ProfileInterest, ProfileInterestAdmin)
admin.site.register(JobListingPrompt, JobListingPromptAdmin)
admin.site.register(Vacancy, VacancyAdmin)

class ExperienceCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector')
    search_fields = ('name',)
    list_filter = ('sector',)
    ordering = ('name',)
    list_per_page = 25

class ExperienceSchoolAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

admin.site.register(ExperienceCompany, ExperienceCompanyAdmin)
admin.site.register(ExperienceSchool, ExperienceSchoolAdmin)