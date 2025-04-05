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
    FavoriteVacancy
)
from accounts.models import ProfileOption

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
        fields = ["id", "name", "skills", "function_skills"]

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

class VacancySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.SerializerMethodField(read_only=True)

    def get_company(self, obj):
        from accounts.serializers import CompanySerializer
        return CompanySerializer(obj.company).data if obj.company else None
    contract_type = ContractTypeSerializer(many=True, read_only=True)
    function = FunctionSerializer(allow_null=True, read_only=True)
    location = LocationSerializer(allow_null=True, read_only=True)
    skill = SkillSerializer(many=True, read_only=True)
    languages = VacancyLanguageSerializer(many=True, read_only=True)
    descriptions = VacancyDescriptionSerializer(many=True, read_only=True)
    questions = VacancyQuestionSerializer(many=True, read_only=True)
    week_day = WeekdaySerializer(many=True, read_only=True)
    salary_benefits = VacancySalaryBenefitSerializer(many=True, read_only=True)
    applicant_count = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    application_status = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "company",
            "created_by",
            "expected_mastery",
            "contract_type",
            "location",
            "function",
            "week_day",
            "job_date",
            "salary",
            "languages",
            "descriptions",
            "questions",
            "skill",
            "salary_benefits",
            "applicant_count",
            "is_favorited",
            "application_status",
            "latitude",
            "longitude",
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
        
        if not self.initial_data.get('location'):
            errors['location'] = 'This field is required.'
        
        if not self.initial_data.get('function'):
            errors['function'] = 'This field is required.'

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def _handle_relationships(self, vacancy, validated_data):
        """
        Handle all relationships for vacancy creation/update
        """
        # Handle one-to-one relationships
        function_data = self.initial_data.get("function", {})
        if function_data and 'id' in function_data:
            vacancy.function = Function.objects.get(id=function_data['id'])

        location_data = self.initial_data.get("location", {})
        if location_data and 'id' in location_data:
            vacancy.location = Location.objects.get(id=location_data['id'])

        # Handle many-to-many relationships
        contract_type_data = self.initial_data.get("contract_type", [])
        if contract_type_data:
            contract_type_ids = [ct.get('id') for ct in contract_type_data if 'id' in ct]
            contract_types = ContractType.objects.filter(id__in=contract_type_ids)
            vacancy.contract_type.set(contract_types)

        skill_data = self.initial_data.get("skill", [])
        if skill_data:
            skill_ids = [skill.get('id') for skill in skill_data if 'id' in skill]
            skills = Skill.objects.filter(id__in=skill_ids)
            vacancy.skill.set(skills)

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
    employee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=ProfileOption.EMPLOYEE),
        many=False
    )
    vacancy = serializers.PrimaryKeyRelatedField(
        queryset=Vacancy.objects.all(),
        many=False
    )
    status = serializers.ChoiceField(choices=ApplicationStatus.choices, read_only=True)
    applied_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ApplyVacancy
        fields = ["id", "employee", "vacancy", "status", "notes", "applied_at", "updated_at"]
        read_only_fields = ["status", "applied_at", "updated_at"]

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
