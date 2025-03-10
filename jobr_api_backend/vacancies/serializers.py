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
    """
    Serializer for the Extra model.
    
    This serializer converts Extra model instances into JSON format for API responses.
    It also validates data for creating or updating Extra instances.

    Meta:
        model: Extra
        fields: ["extra"]
    """
    class Meta:
        model = Extra
        fields = ["extra"]


class VacancyLanguageSerializer(serializers.ModelSerializer):
    """
    Serializer for the VacancyLanguage model.
    
    This serializer converts VacancyLanguage model instances into JSON format for API responses.
    It also validates data for creating or updating VacancyLanguage instances.

    Meta:
        model: VacancyLanguage
        fields: ["language", "mastery"]
    """
    class Meta:
        model = VacancyLanguage
        fields = ["language", "mastery"]


class VacancyDescriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the VacancyDescription model.
    
    This serializer converts VacancyDescription model instances into JSON format for API responses.
    It also validates data for creating or updating VacancyDescription instances.

    Meta:
        model: VacancyDescription
        fields: ["question", "description"]
    """
    class Meta:
        model = VacancyDescription
        fields = ["question", "description"]


class VacancyQuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for the VacancyQuestion model.
    
    This serializer converts VacancyQuestion model instances into JSON format for API responses.
    It also validates data for creating or updating VacancyQuestion instances.

    Meta:
        model: VacancyQuestion
        fields: ["question"]
    """
    class Meta:
        model = VacancyQuestion
        fields = ["question"]


class WeekdaySerializer(serializers.ModelSerializer):
    """
    Serializer for the Weekday model.
    
    This serializer converts Weekday model instances into JSON format for API responses.
    It also validates data for creating or updating Weekday instances.

    Meta:
        model: Weekday
        fields: ["name"]
    """
    class Meta:
        model = Weekday
        fields = ["name"]


class VacancySerializer(serializers.ModelSerializer):
    """
    Serializer for the Vacancy model.

    This serializer is responsible for converting Vacancy model instances into JSON format for API 
    responses and validating data for creating or updating Vacancy instances.

    The serializer includes nested serializers for related models like contract type, function, 
    location, skills, languages, descriptions, questions, and weekdays.

    Fields:
        - employer: The user who is the employer for the vacancy (read-only).
        - contract_type: The types of contracts for the vacancy (many-to-many relation).
        - function: The job function associated with the vacancy.
        - location: The location of the vacancy.
        - skill: The skills required for the vacancy (many-to-many relation).
        - languages: Languages required for the vacancy (many-to-many relation).
        - descriptions: Descriptions related to the vacancy (many-to-many relation).
        - questions: Questions associated with the vacancy (many-to-many relation).
        - week_day: The days of the week the vacancy is available (many-to-many relation).
        - expected_mastery: The expected level of mastery for the position.
        - job_date: The date the vacancy is posted.
        - salary: The salary for the position.

    Methods:
        create(self, validated_data): Create a new Vacancy instance and handle related data for languages, descriptions, 
        questions, week days, and skills.
    """
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
        """
        Create a new Vacancy instance and handle related data for languages, descriptions, 
        questions, week days, and skills.

        This method takes the validated data from the serializer, processes related fields (languages, 
        descriptions, questions, etc.), and creates instances for each of the related models. It then 
        creates the Vacancy instance and associates the related objects.

        Steps:
            1. Retrieve and process related data (languages, descriptions, etc.).
            2. Create or retrieve related objects (Location, Function, Weekday, etc.).
            3. Create the Vacancy instance with the remaining validated data.
            4. Create and associate the related instances (languages, descriptions, skills, etc.).
        
        Parameters:
            validated_data (dict): The validated data that will be used to create the Vacancy instance.
        
        Returns:
            Vacancy: The newly created Vacancy instance with all associated related models.
        """
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
