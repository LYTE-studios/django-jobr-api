from django.db import models
from django.conf import settings


class Sector(models.Model):
    """
    Represents a business sector that groups related functions.
    
    Attributes:
        name (CharField): The name of the sector.
        weight (IntegerField): An optional field that stores the weight of the sector. Defaults to None.
    """
    name = models.CharField(max_length=255, unique=True)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.name} at {self.weight}"


class Location(models.Model):
    """
    Represents a location in the system with an associated weight.
    """
    location = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.location} at {self.weight}"


class ContractType(models.Model):
    """
    Represents the type of contract with an associated weight.
    """
    contract_type = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.contract_type} at {self.weight}"


class Skill(models.Model):
    """
    Represents a skill with an associated category (either 'hard' or 'soft').
    Skills can be associated with multiple Functions with different weights.
    """
    skill = models.CharField(max_length=255)
    category = models.CharField(
        max_length=10, choices=[("hard", "Hard"), ("soft", "Soft")], default="hard"
    )

    def __str__(self):
        return f"{self.skill} - {self.category}"


class FunctionSkill(models.Model):
    """
    Through model for Function-Skill relationship that includes a weight.
    This allows the same skill to have different weights for different functions.
    
    Example:
        "Washing dishes" skill might have:
        - weight=10 for "Dish washing" function
        - weight=2 for "Bartending" function
    """
    function = models.ForeignKey('Function', on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    weight = models.IntegerField(default=1, help_text="Weight of this skill for this specific function")

    class Meta:
        unique_together = ('function', 'skill')
        ordering = ['-weight']  # Order by weight descending

    def __str__(self):
        return f"{self.skill} for {self.function} (weight: {self.weight})"


class Function(models.Model):
    """
    Represents a job function with an associated weight and sector.
    Functions can have multiple skills with different weights for each skill.
    """
    function = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='functions', null=True, blank=True)
    skills = models.ManyToManyField(Skill, through=FunctionSkill, related_name='functions')

    def __str__(self):
        return f"{self.function} at {self.weight}"


class Question(models.Model):
    """
    Represents a question with an associated weight.
    """
    question = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.question} at {self.weight}"


class Language(models.Model):
    """
    Represents a language with an associated weight.
    """
    language = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.language} at {self.weight}"


class MasteryOption(models.TextChoices):
    """
    Enum for representing the different levels of mastery in a skill.
    """
    NONE = "None"
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class Weekday(models.Model):
    """
    Represents a day of the week.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class SalaryBenefit(models.Model):
    """
    Represents a salary-related benefit with a corresponding weight.
    """
    name = models.CharField(max_length=255, unique=True)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.name} at {self.weight}"


class ProfileInterest(models.Model):
    """
    Represents an interest or preference related to a profile, with a weight.
    """
    name = models.CharField(max_length=255, unique=True)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.name} at {self.weight}"


class JobListingPrompt(models.Model):
    """
    Represents a prompt used in job listings.
    """
    name = models.CharField(max_length=255, unique=True)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.name} at {self.weight}"


class VacancyLanguage(models.Model):
    """
    Represents the language requirement for a vacancy.
    """
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    mastery = models.CharField(max_length=255, choices=MasteryOption.choices)


class VacancyDescription(models.Model):
    """
    Represents a description for a vacancy.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    description = models.TextField()


class VacancyQuestion(models.Model):
    """
    Represents a question related to a vacancy.
    """
    question = models.CharField(max_length=255)


class Vacancy(models.Model):
    """
    Represents a job vacancy posted by an employer.
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
    week_day = models.ManyToManyField(Weekday, blank=True)
    job_date = models.DateField(null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    languages = models.ManyToManyField(
        VacancyLanguage, related_name="vacancy_languages"
    )
    descriptions = models.ManyToManyField(VacancyDescription)
    questions = models.ManyToManyField(VacancyQuestion)
    skill = models.ManyToManyField(Skill)
    salary_benefits = models.ManyToManyField(SalaryBenefit, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)


class ApplyVacancy(models.Model):
    """
    Represents an application for a job vacancy by an employee.
    """
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
