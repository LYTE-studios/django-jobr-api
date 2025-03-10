from django.db import models
from django.conf import settings


class Location(models.Model):
    """
    Represents a location in the system with an associated weight.
    
    Attributes:
        location (CharField): A string field that stores the name of the location. The maximum length is 255 characters.
        weight (IntegerField): An optional field that stores the weight of the location. Defaults to None.
    
    Methods:
        __str__(self): Returns a string representation of the Location in the format: "Location at weight".
    """
    location = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        """
        Returns a string representation of the Location in the format:
        "Location at weight".
        
        Returns:
            str: A human-readable string that represents the Location instance.
        """
        return f"{self.location} at {self.weight}"


class ContractType(models.Model):
    """
    Represents the type of contract with an associated weight.
    
    Attributes:
        contract_type (CharField): A string field that stores the type of contract. The maximum length is 255 characters.
        weight (IntegerField): An optional field that stores the weight of the contract type. Defaults to None.
    
    Methods:
        __str__(self): Returns a string representation of the ContractType in the format: "ContractType at weight".
    """
    contract_type = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        """
        Returns a string representation of the ContractType in the format:
        "ContractType at weight".
        
        Returns:
            str: A human-readable string that represents the ContractType instance.
        """
        return f"{self.contract_type} at {self.weight}"


class Function(models.Model):
    """
    Represents a job function with an associated weight.
    
    Attributes:
        function (CharField): A string field that stores the job function. The maximum length is 255 characters.
        weight (IntegerField): An optional field that stores the weight of the function. Defaults to None.
    
    Methods:
        __str__(self): Returns a string representation of the Function in the format: "Function at weight".
    """
    function = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        """
        Returns a string representation of the Function in the format:
        "Function at weight".
        
        Returns:
            str: A human-readable string that represents the Function instance.
        """
        return f"{self.function} at {self.weight}"


class Question(models.Model):
    """
    Represents a question with an associated weight.
    
    Attributes:
        question (CharField): A string field that stores the question text. The maximum length is 255 characters.
        weight (IntegerField): An optional field that stores the weight of the question. Defaults to None.
    
    Methods:
        __str__(self): Returns a string representation of the Question in the format: "Question at weight".
    """
    question = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        """
        Returns a string representation of the Question in the format:
        "Question at weight".
        
        Returns:
            str: A human-readable string that represents the Question instance.
        """
        return f"{self.question} at {self.weight}"


class Language(models.Model):
    """
    Represents a language with an associated weight.
    
    Attributes:
        language (CharField): A string field that stores the name of the language. The maximum length is 255 characters.
        weight (IntegerField): An optional field that stores the weight of the language. Defaults to None.
    
    Methods:
        __str__(self): Returns a string representation of the Language in the format: "Language at weight".
    """
    language = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        """
        Returns a string representation of the Language in the format:
        "Language at weight".
        
        Returns:
            str: A human-readable string that represents the Language instance.
        """
        return f"{self.language} at {self.weight}"

class Skill(models.Model):
    """
    Represents a skill with an associated category (either 'hard' or 'soft') and a weight.
    
    Attributes:
        skill (CharField): A string field that stores the name of the skill. The maximum length is 255 characters.
        category (CharField): A string field with two possible choices ('hard' or 'soft') to specify the type of skill.
        weight (IntegerField): An optional field that stores the weight of the skill. Defaults to None.
    
    Methods:
        __str__(self): Returns a string representation of the Skill in the format: "Skill - Category at weight".
    """
    skill = models.CharField(max_length=255)
    category = models.CharField(
        max_length=10, choices=[("hard", "Hard"), ("soft", "Soft")], default="hard"
    )
    weight = models.IntegerField(null=True)

    def __str__(self):
        """
        Returns a string representation of the Skill in the format:
        "Skill - Category at weight".
        
        Returns:
            str: A human-readable string that represents the Skill instance.
        """
        return f"{self.skill} - {self.category} at {self.weight}"


class MasteryOption(models.TextChoices):
    NONE = "None"
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class Weekday(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
class SalaryBenefit(models.Model):
    name = models.CharField(max_length=255, unique=True)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.name} at {self.weight}"

class ProfileInterest(models.Model):
    name = models.CharField(max_length=255, unique=True)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.name} at {self.weight}"
    
class JobListingPrompt(models.Model):
    name = models.CharField(max_length=255, unique=True)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.name} at {self.weight}"

class VacancyLanguage(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    mastery = models.CharField(max_length=255, choices=MasteryOption.choices)


class VacancyDescription(models.Model):
    # If this value is null, it means the description is presumed to be the main description
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    description = models.TextField()


class VacancyQuestion(models.Model):
    question = models.CharField(max_length=255)


class Vacancy(models.Model):

    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    expected_mastery = models.CharField(
        max_length=255, choices=MasteryOption.choices, null=True
    )

    contract_type = models.ManyToManyField(ContractType, blank=True)

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, blank=True, null=True
    )
    function = models.ForeignKey(
        Function, on_delete=models.CASCADE, blank=True, null=True
    )

    week_day = models.ManyToManyField(Weekday, null=True)
    job_date = models.DateField(null=True)

    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    languages = models.ManyToManyField(
        VacancyLanguage, related_name="vacancy_languages"
    )

    descriptions = models.ManyToManyField(VacancyDescription)

    questions = models.ManyToManyField(VacancyQuestion)

    skill = models.ManyToManyField(Skill)


class ApplyVacancy(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
