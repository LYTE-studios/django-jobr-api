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
    """
    Serializer for the Location model.
    
    This serializer converts Location model instances into JSON format for API responses.
    It also validates data for creating or updating Location instances.

    Meta:
        model: Location
        fields: ["id", "location"]
    """
    class Meta:
        model = Location
        fields = ["id", "location"]


class ContractTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for the ContractType model.
    
    This serializer converts ContractType model instances into JSON format for API responses.
    It also validates data for creating or updating ContractType instances.

    Meta:
        model: ContractType
        fields: ["id", "contract_type"]
    """
    class Meta:
        model = ContractType
        fields = ["id", "contract_type"]


class FunctionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Function model.
    
    This serializer converts Function model instances into JSON format for API responses.
    It also validates data for creating or updating Function instances.

    Meta:
        model: Function
        fields: ["id", "function"]
    """
    class Meta:
        model = Function
        fields = ["id", "function"]


class LanguageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Language model.
    
    This serializer converts Language model instances into JSON format for API responses.
    It also validates data for creating or updating Language instances.

    Meta:
        model: Language
        fields: ["id", "language"]
    """
    class Meta:
        model = Language
        fields = ["id", "language"]


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Question model.
    
    This serializer converts Question model instances into JSON format for API responses.
    It also validates data for creating or updating Question instances.

    Meta:
        model: Question
        fields: ["question"]
    """
    class Meta:
        model = Question
        fields = ["question"]


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for the Skill model.
    
    This serializer converts Skill model instances into JSON format for API responses.
    It also validates data for creating or updating Skill instances.

    Meta:
        model: Skill
        fields: ["id", "skill", "category"]
    """
    class Meta:
        model = Skill
        fields = ["id", "skill", "category"]


class ExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extra
        fields = ["extra"]


class VacancyLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyLanguage
        fields = ["language", "mastery"]


class VacancyDescriptionSerializer(serializers.ModelSerializer):
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
        fields = ["name"]


class VacancySerializer(serializers.ModelSerializer):
    employer = UserSerializer(read_only=True)
    contract_type = ContractTypeSerializer(many=True)
    function = FunctionSerializer()
    location = LocationSerializer()
    skill = SkillSerializer(many=True)
    languages = VacancyLanguageSerializer(many=True)
    descriptions = VacancyDescriptionSerializer(many=True)
    questions = VacancyQuestionSerializer(many=True)
    week_day = WeekdaySerializer(many=True)

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
        languages_data = validated_data.pop("languages")
        descriptions_data = validated_data.pop("descriptions")
        questions_data = validated_data.pop("questions")
        week_days_data = validated_data.pop("week_day")
        skills_data = validated_data.pop("skill")
        location_data = validated_data.pop("location", None)
        function_data = validated_data.pop("function", None)
        if location_data:
            location = Location.objects.get(**location_data)
            validated_data["location"] = location

        if function_data:
            function = Function.objects.get(**function_data)
            validated_data["function"] = function

        vacancy = Vacancy.objects.create(**validated_data)

        for language_data in languages_data:
            VacancyLanguage.objects.create(**language_data, vacancy=vacancy)

        for description_data in descriptions_data:
            VacancyDescription.objects.create(**description_data, vacancy=vacancy)

        for question_data in questions_data:
            VacancyQuestion.objects.create(**question_data, vacancy=vacancy)

        for week_day_data in week_days_data:
            week_day = Weekday.objects.get(**week_day_data)
            vacancy.week_day.set(week_day)

        vacancy.skill.set(skills_data)

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
