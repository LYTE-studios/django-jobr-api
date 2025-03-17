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
    Location
)
from accounts.models import ProfileOption

User = get_user_model()

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "location"]

class ContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractType
        fields = ["id", "contract_type"]

class FunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Function
        fields = ["id", "function"]

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "language"]

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["question"]

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "skill", "category"]

class WeekdaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Weekday
        fields = ["id", "name"]

class VacancyLanguageSerializer(serializers.ModelSerializer):
    language = LanguageSerializer()

    class Meta:
        model = VacancyLanguage
        fields = ["language", "mastery"]

class VacancyDescriptionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    
    class Meta:
        model = VacancyDescription
        fields = ["question", "description"]

class VacancyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyQuestion
        fields = ["question"]

class VacancySerializer(serializers.ModelSerializer):
    employer = serializers.SerializerMethodField()
    contract_type = ContractTypeSerializer(many=True, read_only=True)
    function = FunctionSerializer(allow_null=True, read_only=True)
    location = LocationSerializer(allow_null=True, read_only=True)
    skill = SkillSerializer(many=True, read_only=True)
    languages = VacancyLanguageSerializer(many=True, read_only=True)
    descriptions = VacancyDescriptionSerializer(many=True, read_only=True)
    questions = VacancyQuestionSerializer(many=True, read_only=True)
    week_day = WeekdaySerializer(many=True, read_only=True)

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "employer",
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
        ]

    def get_employer(self, obj):
        from accounts.serializers import UserSerializer
        return UserSerializer(obj.employer).data

    def create(self, validated_data):
        """
        Create a new Vacancy instance with related objects
        """
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is required")

        # Set employer from authenticated user
        validated_data["employer"] = request.user

        # Handle one-to-one relationships
        function_data = self.initial_data.get("function", {})
        if function_data and 'id' in function_data:
            validated_data["function"] = Function.objects.get(id=function_data['id'])

        location_data = self.initial_data.get("location", {})
        if location_data and 'id' in location_data:
            validated_data["location"] = Location.objects.get(id=location_data['id'])

        # Create the vacancy
        vacancy = Vacancy.objects.create(**validated_data)

        # Handle many-to-many relationships
        contract_type_data = self.initial_data.get("contract_type", [])
        if contract_type_data:
            contract_type_ids = [ct.get('id') for ct in contract_type_data if 'id' in ct]
            contract_types = ContractType.objects.filter(id__in=contract_type_ids)
            vacancy.contract_type.set(contract_types)

        skill_data = self.initial_data.get("skill", [])
        if skill_data:
            skill_ids = [skill.get('id') for skill in skill_data if 'id' in skill]
            vacancy.skill.set(Skill.objects.filter(id__in=skill_ids))

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

        vacancy.save()
        return vacancy

class ApplySerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=ProfileOption.EMPLOYEE),
        many=False
    )
    vacancy = serializers.PrimaryKeyRelatedField(
        queryset=Vacancy.objects.all(),
        many=False
    )

    class Meta:
        model = ApplyVacancy
        fields = ["employee", "vacancy"]
