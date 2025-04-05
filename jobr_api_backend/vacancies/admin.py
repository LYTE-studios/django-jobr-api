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

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m = self._save_m2m
        return instance
    
    def _save_m2m(self):
        # Handle skills
        selected_skills = self.cleaned_data.get('all_skills', [])
        
        # Clear existing relationships but preserve weights
        existing_weights = {
            fs.skill_id: fs.weight
            for fs in FunctionSkill.objects.filter(function=self.instance)
        }
        FunctionSkill.objects.filter(function=self.instance).delete()
        
        # Create new relationships with preserved or default weights
        for skill in selected_skills:
            weight = existing_weights.get(skill.id, 1)  # Use existing weight or default to 1
            FunctionSkill.objects.create(
                function=self.instance,
                skill=skill,
                weight=weight
            )

@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    form = FunctionAdminForm
    list_display = ('name', 'weight', 'get_sectors', 'get_skills_count')
    search_fields = ('name', 'sectors__name', 'skills__name')
    list_filter = ('weight', 'sectors')
    ordering = ('name',)
    list_per_page = 25
    change_form_template = 'admin/vacancies/function/change_form.html'

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
                '<int:function_id>/edit-weights/',
                self.admin_site.admin_view(self.edit_weights_view),
                name='edit-function-skill-weights',
            ),
        ]
        return custom_urls + urls

    def edit_weights_view(self, request, function_id):
        function = self.get_object(request, function_id)
        
        if not function:
            raise Http404("Function does not exist")

        class SkillWeightForm(forms.Form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for skill in function.skills.all():
                    weight = FunctionSkill.objects.get(function=function, skill=skill).weight
                    self.fields[f'weight_{skill.id}'] = forms.IntegerField(
                        label=skill.name,
                        initial=weight,
                        min_value=1,
                        required=True
                    )

        if request.method == 'POST':
            form = SkillWeightForm(request.POST)
            if form.is_valid():
                for skill in function.skills.all():
                    weight = form.cleaned_data[f'weight_{skill.id}']
                    function_skill = FunctionSkill.objects.get(
                        function=function,
                        skill=skill
                    )
                    function_skill.weight = weight
                    function_skill.save()
                self.message_user(request, "Skill weights updated successfully.")
                return HttpResponseRedirect(
                    reverse('admin:vacancies_function_changelist')
                )
        else:
            form = SkillWeightForm()

        context = {
            'title': f'Edit Skill Weights for {function}',
            'form': form,
            'opts': self.model._meta,
            'original': function,
            'media': self.media + form.media,
        }
        return TemplateResponse(
            request,
            'admin/vacancies/function/edit_weights.html',
            context,
        )

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