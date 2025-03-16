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
    """
    Enum for representing the different levels of mastery in a skill.
    
    This class is used to define the different stages of skill proficiency. The options range from "None" (no proficiency)
    to "Expert" (highest proficiency).
    
    Choices:
        NONE (str): Represents no proficiency.
        BEGINNER (str): Represents a beginner level of proficiency.
        INTERMEDIATE (str): Represents an intermediate level of proficiency.
        ADVANCED (str): Represents an advanced level of proficiency.
        EXPERT (str): Represents the highest level of proficiency.
    """
    NONE = "None"
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class Weekday(models.Model):
    """
    Represents a day of the week.
    
    Attributes:
        name (CharField): The name of the weekday.
    
    Methods:
        __str__(self): Returns the name of the weekday as a string.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        """
        Returns the name of the weekday as a string.
        
        Returns:
            str: The name of the weekday.
        """
        return self.name
    
class SalaryBenefit(models.Model):
    """
    Represents a salary-related benefit with a corresponding weight.
    
    Attributes:
        name (CharField): A string field that stores the name of the salary benefit.
        weight (IntegerField): An optional field to store the weight of the benefit. Defaults to None.
    
    Methods:
        __str__(self): Returns a string representation of the salary benefit and its weight in the format: "Benefit at weight".
    """
    name = models.CharField(max_length=255, unique=True)
    weight = models.IntegerField(null=True)

    def __str__(self):
        """
        Returns a string representation of the SalaryBenefit in the format:
        "Benefit at weight".
        
        Returns:
            str: A human-readable string representing the SalaryBenefit instance.
        """
        return f"{self.name} at {self.weight}"

class ProfileInterest(models.Model):
    """
    Represents an interest or preference related to a profile, with a weight.
    
    Attributes:
        name (CharField): The name of the interest.
        weight (IntegerField, optional): An optional field that stores the weight of the interest. Defaults to None.
    
    Methods:
        __str__(self): Returns a string representation of the ProfileInterest in the format: "Interest at weight".
    """
    name = models.CharField(max_length=255, unique=True)
    weight = models.IntegerField(null=True)

    def __str__(self):
        """
        Returns a string representation of the ProfileInterest in the format:
        "Interest at weight".
        
        Returns:
            str: A human-readable string representing the ProfileInterest instance.
        """
        return f"{self.name} at {self.weight}"
    
class JobListingPrompt(models.Model):
    """
    Represents a prompt used in job listings, which can be associated with different listings based on its weight.
    
    Attributes:
        name (CharField): The name or description of the prompt (e.g., 'Urgent Hiring', 'Remote Friendly').
        weight (IntegerField, optional): A numeric value representing the weight of the prompt. Defaults to None.
    
    Methods:
        __str__(self): Returns a string representation of the JobListingPrompt in the format: "Prompt at weight".
    """
    name = models.CharField(max_length=255, unique=True)
    weight = models.IntegerField(null=True)

    def __str__(self):
        """
        Returns a string representation of the JobListingPrompt in the format:
        "Prompt at weight".
        
        Returns:
            str: A human-readable string representing the JobListingPrompt instance.
        """
        return f"{self.name} at {self.weight}"

class VacancyLanguage(models.Model):
    """
    Represents the language requirement for a vacancy, including the proficiency level required for that language.
    
    Attributes:
        language (ForeignKey): A reference to the `Language` model, indicating the language required for the vacancy.
        mastery (CharField): A field representing the proficiency level required for the language, using the `MasteryOption` choices.
    """
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    mastery = models.CharField(max_length=255, choices=MasteryOption.choices)


class VacancyDescription(models.Model):
    """
    Represents a description for a vacancy, which could be a main description or an associated description for a specific question.
    
    Attributes:
        question (ForeignKey, optional): A reference to the `Question` model that links a specific question to the vacancy description. If null, the description is considered the main description.
        description (TextField): The text of the vacancy description.
    """
    # If this value is null, it means the description is presumed to be the main description
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    description = models.TextField()


class VacancyQuestion(models.Model):
    """
    Represents a question related to a vacancy that can be used in vacancy descriptions.
    
    Attributes:
        question (CharField): The text of the question to be asked or associated with the vacancy.
    """
    question = models.CharField(max_length=255)


class Vacancy(models.Model):
    """
    Represents a job vacancy posted by an employer.

    Attributes:
        employer (ForeignKey): A reference to the user (employer) who posted the vacancy.
        expected_mastery (CharField): The required mastery level for the vacancy, based on `MasteryOption` choices.
        contract_type (ManyToManyField): The contract types applicable for the vacancy, related to the `ContractType` model.
        location (ForeignKey, optional): The location of the vacancy, linked to the `Location` model. Can be null.
        function (ForeignKey, optional): The function or role for the vacancy, linked to the `Function` model. Can be null.
        week_day (ManyToManyField): The weekdays the vacancy is available, related to the `Weekday` model.
        job_date (DateField, optional): The date the job vacancy is available or applicable. Can be null.
        salary (DecimalField, optional): The salary for the vacancy, with two decimal places. Can be null or blank.
        languages (ManyToManyField): Languages required for the vacancy, related to the `VacancyLanguage` model.
        descriptions (ManyToManyField): The descriptions associated with the vacancy, linked to the `VacancyDescription` model.
        questions (ManyToManyField): A list of questions related to the vacancy, linked to the `VacancyQuestion` model.
        skill (ManyToManyField): The skills required for the vacancy, related to the `Skill` model.
    """

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
    """
    Represents an application for a job vacancy by an employee.

    Attributes:
        employee (ForeignKey): A reference to the employee (user) who applied for the vacancy.
        vacancy (ForeignKey): A reference to the `Vacancy` that the employee has applied for.
    """
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
