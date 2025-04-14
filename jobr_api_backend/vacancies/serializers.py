from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
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

class VacancyDescriptionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    
    class Meta:
        model = VacancyDescription
        fields = ["question", "description"]

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
        # Handle date_times
        date_times_data = self.initial_data.get('date_times_data', [])
        if date_times_data:
            # Clear existing date_times
            vacancy.date_times.all().delete()
            # Create new date_times
            for dt_data in date_times_data:
                VacancyDateTime.objects.create(
                    vacancy=vacancy,
                    date=dt_data['date'],
                    start_time=dt_data['start_time'],
                    end_time=dt_data['end_time']
                )

        # Handle one-to-one relationships using write-only fields
        if 'function' in validated_data:
            vacancy.function = validated_data['function']

        if 'location' in validated_data:
            vacancy.location = validated_data['location']

        # Handle many-to-many relationships using write-only fields
        if 'contract_type' in validated_data:
            vacancy.contract_type.set(validated_data['contract_type'])

        if 'skill' in validated_data:
            vacancy.skill.set(validated_data['skill'])

        if 'salary_benefits' in validated_data:
            vacancy.salary_benefits.set(validated_data['salary_benefits'])

        language_data = self.initial_data.get("languages", [])
        if language_data:
            languages = []
            for lang_data in language_data:
                if 'language' in lang_data and 'mastery' in lang_data:
                    language = Language.objects.get(id=lang_data['language'])
                    languages.append(
                        VacancyLanguage.objects.create(
                            language=language,
                            mastery=lang_data['mastery']
                        )
                    )
            vacancy.languages.set(languages)

        description_data = self.initial_data.get("descriptions", [])
        if description_data:
            descriptions = []
            for desc_data in description_data:
                question = None
                if 'question' in desc_data and desc_data['question']:
                    question = Question.objects.get(id=desc_data['question'])
                descriptions.append(
                    VacancyDescription.objects.create(
                        question=question,
                        description=desc_data.get('description', '')
                    )
                )
            vacancy.descriptions.set(descriptions)

        question_data = self.initial_data.get("questions", [])
        if question_data:
            questions = [
                VacancyQuestion.objects.create(question=q.get('question'))
                for q in question_data if 'question' in q
            ]
            vacancy.questions.set(questions)

        week_day_data = self.initial_data.get("week_day", [])
        if week_day_data:
            week_days = [
                Weekday.objects.get(name=day.get('name'))
                for day in week_day_data if 'name' in day
            ]
            vacancy.week_day.set(week_days)

        # Handle salary benefits
        salary_benefits_data = self.initial_data.get("salary_benefits", [])
        if salary_benefits_data:
            salary_benefit_ids = [sb.get('id') for sb in salary_benefits_data if 'id' in sb]
            salary_benefits = SalaryBenefit.objects.filter(id__in=salary_benefit_ids)
            vacancy.salary_benefits.set(salary_benefits)

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

        # Update simple fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
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
