from rest_framework import serializers
from accounts.models import Employee
from .models import (
    Vacancy,
    ApplyVacancy,
    VacancyLanguage,
    VacancyDescription,
    VacancyQuestion,
    Weekday,
)
from .models import ContractType, Function, Question, Skill, Language, Location
from common.models import Extra
from accounts.serializers import UserSerializer  # Import the UserSerializer


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


class ExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extra
        fields = ["extra"]


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


class WeekdaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Weekday
        fields = ["id", "name"]


class VacancySerializer(serializers.ModelSerializer):
    employer = UserSerializer(read_only=True)
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

    def create(self, validated_data):
        request = self.context.get('request') 

        ## ONE TO ONE RELATIONSHIPS

        # Employer
        validated_data["employer"] = request.user

        # Function
        function = request.data.get("function")
        if function:
            function_id = function.get("id")
            validated_data["function"] = Function.objects.get(id=function_id)

        # Location 
        location_id = request.data.get("location").get("id")
        validated_data["location"] = Location.objects.get(id=location_id) if location_id else None

        # Create the vacancy
        vacancy = Vacancy.objects.create(**validated_data)

        # MANY TO MANY RELATIONSHIPS

        # Contract types
        contract_type_ids = [ct.get('id') for ct in request.data.get("contract_type")]
        contract_types = ContractType.objects.filter(id__in=contract_type_ids)
        vacancy.contract_type.set(contract_types) if contract_types else None

        # Skills
        skill_ids = [skill.get('id') for skill in request.data.get("skill")]
        vacancy.skill.set(Skill.objects.filter(id__in=skill_ids)) if skill_ids else None

        # Languages
        language_ids = [(language.get('language'), language.get('mastery')) for language in request.data.get("languages")]
        languages = []
        for language, mastery in language_ids:
            languages.append(VacancyLanguage.objects.create(language=Language.objects.get(id=language), mastery=mastery))
        vacancy.languages.set(languages) if languages else None

        # Descriptions
        question_ids = [(description.get('question', None), description.get('description')) for description in request.data.get("descriptions")]
        descriptions = []
        for question, description in question_ids:
            descriptions.append(VacancyDescription.objects.create(question=Question.objects.get(id=question), description=description))
        vacancy.descriptions.set(descriptions) if descriptions else None

        # Questions
        questions = [VacancyQuestion.objects.create(question=question.get('question')) for question in request.data.get("questions")]
        vacancy.questions.set(questions) if questions else None

        # Days
        week_days = [Weekday.objects.get(name=day.get('name')) for day in request.data.get("week_day")]
        vacancy.week_day.set(week_days) if week_days else None

        vacancy.save()

        return vacancy

class ApplySerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), many=False
    )
    vacancy = serializers.PrimaryKeyRelatedField(
        queryset=Vacancy.objects.all(), many=False
    )

    class Meta:
        model = ApplyVacancy
        fields = ["employee", "vacancy"]
