from django.contrib import admin
from django.http import HttpResponseRedirect, Http404
from django.template.response import TemplateResponse
from django.urls import reverse
from django import forms
from django.db import transaction
import logging
from .models import (
    Vacancy, Question, ContractType, Function, Language, Skill, Location,
    SalaryBenefit, ProfileInterest, JobListingPrompt, VacancyLanguage,
    VacancyDescription, VacancyQuestion, ApplyVacancy, Weekday, Sector,
    FunctionSkill
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
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['functions'].initial = self.instance.functions.all()

    def save(self, commit=True):
        sector = super().save(commit=False)
        if commit:
            try:
                with transaction.atomic():
                    sector.save()
                    
                    # Handle functions relationship
                    if 'functions' in self.cleaned_data:
                        current_functions = set(sector.functions.values_list('id', flat=True))
                        new_functions = set(f.id for f in self.cleaned_data['functions'])
                        
                        # Log current state
                        logger.info(f"Current functions for sector {sector.pk}: {current_functions}")
                        logger.info(f"New functions for sector {sector.pk}: {new_functions}")
                        
                        # Remove functions that are no longer selected
                        to_remove = current_functions - new_functions
                        if to_remove:
                            logger.info(f"Removing functions from sector {sector.pk}: {to_remove}")
                            sector.functions.remove(*to_remove)
                        
                        # Add newly selected functions
                        to_add = new_functions - current_functions
                        if to_add:
                            logger.info(f"Adding functions to sector {sector.pk}: {to_add}")
                            sector.functions.add(*to_add)
                        
                        # Verify changes
                        final_functions = set(sector.functions.values_list('id', flat=True))
                        logger.info(f"Final functions for sector {sector.pk}: {final_functions}")
                        
                        if final_functions != new_functions:
                            error_msg = (
                                f"Functions were not saved correctly. "
                                f"Expected: {new_functions}, "
                                f"Got: {final_functions}"
                            )
                            if self.request:
                                from django.contrib import messages
                                messages.error(self.request, error_msg)
                            raise ValueError(error_msg)
                            
            except Exception as e:
                logger.error(f"Error saving sector {sector.pk}: {str(e)}")
                if self.request:
                    from django.contrib import messages
                    messages.error(self.request, f"Error saving sector: {str(e)}")
                raise
        return sector

class SectorAdmin(admin.ModelAdmin):
    form = SectorAdminForm
    list_display = ('name', 'weight', 'enabled', 'get_functions_count')
    search_fields = ('name', 'functions__name')
    list_filter = ('weight', 'enabled')
    ordering = ('name',)
    list_per_page = 25

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

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
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['sectors'].initial = self.instance.sectors.all()
            self.fields['all_skills'].initial = self.instance.skills.all()

    def save(self, commit=True):
        function = super().save(commit=False)
        if commit:
            try:
                with transaction.atomic():
                    function.save()
                    
                    # Handle sectors relationship
                    if 'sectors' in self.cleaned_data:
                        current_sectors = set(function.sectors.values_list('id', flat=True))
                        new_sectors = set(s.id for s in self.cleaned_data['sectors'])
                        
                        # Log current state
                        logger.info(f"Current sectors for function {function.pk}: {current_sectors}")
                        logger.info(f"New sectors for function {function.pk}: {new_sectors}")
                        
                        # Remove sectors that are no longer selected
                        to_remove = current_sectors - new_sectors
                        if to_remove:
                            logger.info(f"Removing sectors from function {function.pk}: {to_remove}")
                            function.sectors.remove(*to_remove)
                        
                        # Add newly selected sectors
                        to_add = new_sectors - current_sectors
                        if to_add:
                            logger.info(f"Adding sectors to function {function.pk}: {to_add}")
                            function.sectors.add(*to_add)
                        
                        # Verify changes
                        final_sectors = set(function.sectors.values_list('id', flat=True))
                        logger.info(f"Final sectors for function {function.pk}: {final_sectors}")
                        
                        if final_sectors != new_sectors:
                            error_msg = (
                                f"Sectors were not saved correctly. "
                                f"Expected: {new_sectors}, "
                                f"Got: {final_sectors}"
                            )
                            if self.request:
                                from django.contrib import messages
                                messages.error(self.request, error_msg)
                            raise ValueError(error_msg)
                    
                    # Handle skills relationship
                    if 'all_skills' in self.cleaned_data:
                        current_skills = set(function.skills.values_list('id', flat=True))
                        new_skills = set(s.id for s in self.cleaned_data['all_skills'])
                        
                        # Log current state
                        logger.info(f"Current skills for function {function.pk}: {current_skills}")
                        logger.info(f"New skills for function {function.pk}: {new_skills}")
                        
                        # Preserve existing weights
                        existing_weights = {
                            fs.skill_id: fs.weight
                            for fs in FunctionSkill.objects.filter(function=function)
                        }
                        
                        # Remove skills that are no longer selected
                        FunctionSkill.objects.filter(
                            function=function,
                            skill_id__in=current_skills - new_skills
                        ).delete()
                        
                        # Add or update selected skills
                        for skill_id in new_skills:
                            FunctionSkill.objects.update_or_create(
                                function=function,
                                skill_id=skill_id,
                                defaults={'weight': existing_weights.get(skill_id, 1)}
                            )
                        
                        # Verify changes
                        final_skills = set(function.skills.values_list('id', flat=True))
                        logger.info(f"Final skills for function {function.pk}: {final_skills}")
                        
                        if final_skills != new_skills:
                            error_msg = (
                                f"Skills were not saved correctly. "
                                f"Expected: {new_skills}, "
                                f"Got: {final_skills}"
                            )
                            if self.request:
                                from django.contrib import messages
                                messages.error(self.request, error_msg)
                            raise ValueError(error_msg)
                            
            except Exception as e:
                logger.error(f"Error saving function {function.pk}: {str(e)}")
                if self.request:
                    from django.contrib import messages
                    messages.error(self.request, f"Error saving function: {str(e)}")
                raise
        return function

class FunctionAdmin(admin.ModelAdmin):
    form = FunctionAdminForm
    list_display = ('name', 'weight', 'get_sectors', 'get_skills_count')
    search_fields = ('name', 'sectors__name', 'skills__name')
    list_filter = ('weight', 'sectors')
    ordering = ('name',)
    list_per_page = 25
    change_form_template = 'admin/vacancies/function/change_form.html'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

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
        ]
        return custom_urls + urls

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