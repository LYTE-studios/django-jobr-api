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
        fields = ["id", "name"]


class VacancySerializer(serializers.ModelSerializer):
    employer = UserSerializer(read_only=True)
    contract_type = ContractTypeSerializer(many=True)
    function = FunctionSerializer(allow_null=True)
    location = LocationSerializer(allow_null=True)
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
        request = self.context.get('request')
        if request and hasattr(request.user, 'employer_profile'):
            validated_data['employer'] = request.user
        else:
            raise serializers.ValidationError("User does not have an employer profile.")

        languages_data = validated_data.pop("languages")
        descriptions_data = validated_data.pop("descriptions")
        questions_data = validated_data.pop("questions")
        week_days_data = validated_data.pop("week_day")
        skills_data = validated_data.pop("skill")
        contract_types_data = validated_data.pop("contract_type")

        vacancy = Vacancy.objects.create(**validated_data)

        for language_data in languages_data:
            language = VacancyLanguage.objects.create(**language_data)
            vacancy.languages.add(language)

        for description_data in descriptions_data:
            description = VacancyDescription.objects.create(**description_data)
            vacancy.descriptions.add(description)

        for question_data in questions_data:
            question = VacancyQuestion.objects.create(**question_data)
            vacancy.questions.add(question)

        vacancy.skill.set(skills_data)
        vacancy.week_day.set(week_days_data)
        vacancy.contract_type.set(contract_types_data)

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
