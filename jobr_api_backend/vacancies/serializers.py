from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    JobListingPrompt,
    Vacancy,
    ApplyVacancy,
    VacancyLanguage,
    VacancyDescription,
    VacancyQuestion,
    Weekday,
    ContractType,
    Function,
    Question,
    Skill,
    Language,
    Location,
    ProfileInterest,
    SalaryBenefit,
    FunctionSkill,
    Sector,
    ApplicationStatus,
    FavoriteVacancy,
    VacancyDateTime
)
from accounts.models import ProfileOption, Employee

User = get_user_model()

class SectorSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = Sector
        fields = ['id', 'name', 'weight', 'enabled', 'icon_url']

    def get_icon_url(self, obj):
        return obj.icon.url if obj.icon else None

class SalaryBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryBenefit
        fields = ('id', 'name', 'weight')

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name"]

class ContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractType
        fields = ["id", "name"]

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "category"]

class FunctionSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer()
    
    class Meta:
        model = FunctionSkill
        fields = ["skill", "weight"]

class FunctionSerializer(serializers.ModelSerializer):
    function_skills = FunctionSkillSerializer(source='functionskill_set', many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Function
        fields = ["id", "name", "weight", "skills", "function_skills"]

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "name"]

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "name"]

class WeekdaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Weekday
        fields = ["id", "name"]

class VacancyLanguageSerializer(serializers.ModelSerializer):
    language = LanguageSerializer()

    class Meta:
        model = VacancyLanguage
        fields = ["language", "mastery"]

    def validate_mastery(self, value):
        """Capitalize the mastery value before validation."""
        return value.capitalize() if value else value

class VacancyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyQuestion
        fields = ["question"]

class ProfileInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileInterest
        fields = ["id", "name"]

class VacancySalaryBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryBenefit
        fields = ["id", "name"]

class JobListingPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobListingPrompt
        fields = ['id', 'name', 'weight']

class VacancyDescriptionSerializer(serializers.ModelSerializer):
    prompt = JobListingPromptSerializer(read_only=True)
    prompt_id = serializers.PrimaryKeyRelatedField(
        queryset=JobListingPrompt.objects.all(),
        source='prompt',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = VacancyDescription
        fields = ["prompt", "prompt_id", "description"]

class VacancyDateTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyDateTime
        fields = ['id', 'date', 'start_time', 'end_time']

class VacancySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.SerializerMethodField(read_only=True)
    date_times = VacancyDateTimeSerializer(many=True, read_only=True)

    def get_company(self, obj):
        from accounts.serializers import CompanySerializer
        return CompanySerializer(obj.company).data if obj.company else None
    # Read-only nested serializers for detailed representation
    contract_type = ContractTypeSerializer(many=True, read_only=True)
    function = FunctionSerializer(allow_null=True, read_only=True)
    location = LocationSerializer(allow_null=True, read_only=True)
    skill = SkillSerializer(many=True, read_only=True)
    languages = VacancyLanguageSerializer(many=True, read_only=True)
    descriptions = VacancyDescriptionSerializer(many=True, read_only=True)
    questions = VacancyQuestionSerializer(many=True, read_only=True)
    week_day = WeekdaySerializer(many=True, read_only=True)
    salary_benefits = VacancySalaryBenefitSerializer(many=True, read_only=True)

    # Write fields for updates
    contract_type_ids = serializers.PrimaryKeyRelatedField(
        queryset=ContractType.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='contract_type'
    )
    function_id = serializers.PrimaryKeyRelatedField(
        queryset=Function.objects.all(),
        write_only=True,
        required=False,
        source='function'
    )
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        write_only=True,
        required=False,
        source='location'
    )
    skill_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='skill'
    )
    salary_benefit_ids = serializers.PrimaryKeyRelatedField(
        queryset=SalaryBenefit.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='salary_benefits'
    )
    date_times_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    applicant_count = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    application_status = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "company",
            "created_by",
            "title",
            "description",
            "internal_function_title",
            "expected_mastery",
            "contract_type", "contract_type_ids",
            "location", "location_id",
            "function", "function_id",
            "week_day",
            "date_times", "date_times_data",
            "salary",
            "languages",
            "descriptions",
            "questions",
            "skill", "skill_ids",
            "salary_benefits", "salary_benefit_ids",
            "responsibilities",
            "applicant_count",
            "is_favorited",
            "application_status",
            "latitude",
            "longitude",
        ]
        read_only_fields = [
            "company",
            "created_by",
            "applicant_count",
            "is_favorited",
            "application_status"
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and hasattr(request.user, 'employee_profile'):
            return FavoriteVacancy.objects.filter(
                employee=request.user.employee_profile,
                vacancy=obj
            ).exists()
        return False

    def get_application_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and hasattr(request.user, 'employee_profile'):
            application = ApplyVacancy.objects.filter(
                employee=request.user.employee_profile,
                vacancy=obj
            ).first()
            if application:
                return {
                    'status': application.status,
                    'applied_at': application.applied_at,
                    'updated_at': application.updated_at,
                    'notes': application.notes
                }
        return None

    def get_applicant_count(self, obj):
        return ApplyVacancy.objects.filter(vacancy=obj).count()
    
    def get_created_by(self, obj):
        from accounts.serializers import UserSerializer
        return UserSerializer(obj.created_by).data if obj.created_by else None

    def validate_expected_mastery(self, value):
        """Capitalize the mastery value before validation."""
        return value.capitalize() if value else value

    def validate(self, data):
        """
        Validate required fields for vacancy creation
        """
        errors = {}
        
        # Check required fields in initial data
        if not self.initial_data.get('expected_mastery'):
            errors['expected_mastery'] = 'This field is required.'
        
        # Check location (either location or location_id must be provided)
        if not (self.initial_data.get('location') or self.initial_data.get('location_id')):
            errors['location'] = 'Location is required.'
        
        # Check function (either function or function_id must be provided)
        if not (self.initial_data.get('function') or self.initial_data.get('function_id')):
            errors['function'] = 'Function is required.'

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def _handle_relationships(self, vacancy, validated_data):
        """
        Handle all relationships for vacancy creation/update
        """
        # Handle basic fields
        for field in ['title', 'description', 'internal_function_title', 'expected_mastery', 'salary', 'responsibilities']:
            if field in self.initial_data:
                setattr(vacancy, field, self.initial_data[field])

        # Handle one-to-one relationships
        function_data = self.initial_data.get('function')
        if function_data and 'id' in function_data:
            vacancy.function = Function.objects.get(id=function_data['id'])

        location_data = self.initial_data.get('location')
        if location_data and 'id' in location_data:
            vacancy.location = Location.objects.get(id=location_data['id'])

        # Handle many-to-many relationships
        # Handle contract types
        contract_type_data = self.initial_data.get('contract_type', [])
        if contract_type_data:
            contract_type_ids = [ct['id'] for ct in contract_type_data if 'id' in ct]
            vacancy.contract_type.set(contract_type_ids)

        # Handle skills
        skill_data = self.initial_data.get('skill', [])
        if skill_data:
            skill_ids = [skill['id'] for skill in skill_data if 'id' in skill]
            vacancy.skill.set(skill_ids)

        # Handle salary benefits
        salary_benefits_data = self.initial_data.get('salary_benefits', [])
        if salary_benefits_data:
            salary_benefit_ids = [sb['id'] for sb in salary_benefits_data if 'id' in sb]
            vacancy.salary_benefits.set(salary_benefit_ids)

        # Handle week days
        week_day_data = self.initial_data.get('week_day', [])
        if week_day_data:
            week_day_ids = [wd['id'] for wd in week_day_data if 'id' in wd]
            vacancy.week_day.set(week_day_ids)

        # Handle languages
        languages_data = self.initial_data.get('languages', [])
        if languages_data:
            vacancy.languages.clear()  # Clear existing languages
            for lang_data in languages_data:
                if 'language' in lang_data and 'mastery' in lang_data:
                    lang = VacancyLanguage.objects.create(
                        language_id=lang_data['language'],
                        mastery=lang_data['mastery']
                    )
                    vacancy.languages.add(lang)

        # Handle descriptions
        descriptions_data = self.initial_data.get('descriptions', [])
        if descriptions_data:
            vacancy.descriptions.clear()  # Clear existing descriptions
            for desc_data in descriptions_data:
                description = VacancyDescription.objects.create(
                    description=desc_data.get('description', '')
                )
                if 'prompt' in desc_data:
                    description.prompt_id = desc_data['prompt']
                    description.save()
                vacancy.descriptions.add(description)
        # Handle questions
        questions_data = self.initial_data.get('questions', [])
        if questions_data:
            vacancy.questions.clear()  # Clear existing questions
            for q_data in questions_data:
                question = VacancyQuestion.objects.create(
                    question=q_data.get('question', '')
                )
                vacancy.questions.add(question)

        vacancy.save()
        return vacancy

    def create(self, validated_data):
        """
        Create a new Vacancy instance with related objects
        """
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is required")

        # Create the vacancy
        vacancy = Vacancy.objects.create(**validated_data)
        return self._handle_relationships(vacancy, validated_data)

    def update(self, instance, validated_data):
        """
        Update a Vacancy instance and its related objects
        """
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is required")

        # Update basic fields from validated_data
        for field in validated_data:
            if hasattr(instance, field):
                setattr(instance, field, validated_data[field])
        
        # Handle all relationships and save
        return self._handle_relationships(instance, validated_data)

class ApplySerializer(serializers.ModelSerializer):
    # Write operations (when creating/updating applications)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )
    vacancy_id = serializers.PrimaryKeyRelatedField(
        queryset=Vacancy.objects.all(),
        source='vacancy',
        write_only=True
    )
    
    # Read operations (when fetching applications)
    employee = serializers.SerializerMethodField(read_only=True)
    vacancy = VacancySerializer(read_only=True)
    status = serializers.ChoiceField(choices=ApplicationStatus.choices, read_only=True)
    applied_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ApplyVacancy
        fields = [
            "id",
            "employee", "employee_id",
            "vacancy", "vacancy_id",
            "status",
            "notes",
            "applied_at",
            "updated_at"
        ]
        read_only_fields = ["status", "applied_at", "updated_at", "employee", "vacancy"]

    def get_employee(self, obj):
        from accounts.serializers import UserSerializer
        return UserSerializer(obj.employee.user).data

class FavoriteVacancySerializer(serializers.ModelSerializer):
    vacancy = VacancySerializer(read_only=True)
    vacancy_id = serializers.PrimaryKeyRelatedField(
        queryset=Vacancy.objects.all(),
        source='vacancy',
        write_only=True
    )

    class Meta:
        model = FavoriteVacancy
        fields = ['id', 'vacancy', 'vacancy_id', 'created_at']
        read_only_fields = ['created_at']
