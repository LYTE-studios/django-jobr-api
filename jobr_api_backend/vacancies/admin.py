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

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name',)
    list_filter = ('weight',)
    ordering = ('name',)
    list_per_page = 25

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

    class Meta:
        model = Function
        fields = '__all__'
        exclude = ('skills',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['all_skills'].initial = self.instance.skills.all()
            # Add weight fields for existing skills
            for skill in self.instance.skills.all():
                field_name = f'weight_{skill.id}'
                self.fields[field_name] = forms.IntegerField(
                    label=f'Weight for {skill.name}',
                    initial=FunctionSkill.objects.get(function=self.instance, skill=skill).weight,
                    min_value=1,
                    required=False
                )
        
        # Add weight fields for any skills in POST data
        if 'all_skills' in self.data:
            skill_ids = self.data.getlist('all_skills')
            for skill_id in skill_ids:
                try:
                    skill = Skill.objects.get(id=skill_id)
                    field_name = f'weight_{skill.id}'
                    if field_name not in self.fields:
                        self.fields[field_name] = forms.IntegerField(
                            label=f'Weight for {skill.name}',
                            initial=1,
                            min_value=1,
                            required=False
                        )
                except Skill.DoesNotExist:
                    pass

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Clear existing skills to prepare for new ones
            FunctionSkill.objects.filter(function=instance).delete()
            # Add new skills with specified weights
            for skill in self.cleaned_data['all_skills']:
                weight = self.cleaned_data.get(f'weight_{skill.id}', 1)
                FunctionSkill.objects.create(
                    function=instance,
                    skill=skill,
                    weight=weight
                )
        return instance

@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    form = FunctionAdminForm
    list_display = ('name', 'weight', 'sector', 'get_skills_count')
    search_fields = ('name', 'sector__name')
    list_filter = ('weight', 'sector')
    ordering = ('name',)
    list_per_page = 25
    actions = ['edit_skill_weights']

    def get_skills_count(self, obj):
        return obj.skills.count()
    get_skills_count.short_description = 'Skills'

    def edit_skill_weights(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one function to edit skill weights.", level='ERROR')
            return
        
        function = queryset.first()
        return HttpResponseRedirect(
            reverse('admin:edit-function-skill-weights', args=[function.pk])
        )
    edit_skill_weights.short_description = "Edit skill weights for selected function"

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
        from django import forms
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
                    FunctionSkill.objects.filter(
                        function=function,
                        skill=skill
                    ).update(weight=weight)
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
    list_display = ('title', 'employer', 'function', 'location', 'job_date', 'salary', 'expected_mastery')
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
        'employer__user__username',
        'employer__user__email',
        'function__name',
        'location__name',
    )
    filter_horizontal = ('contract_type', 'week_day', 'languages', 'descriptions', 'questions', 'skill')
    raw_id_fields = ('employer',)
    date_hierarchy = 'job_date'
    list_per_page = 25