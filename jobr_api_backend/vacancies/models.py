from django.db import models
from django.conf import settings


class Location(models.Model):
    location = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.location} at {self.weight}"


class ContractType(models.Model):
    contract_type = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.contract_type} at {self.weight}"


class Function(models.Model):
    function = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.function} at {self.weight}"


class Question(models.Model):
    question = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.question} at {self.weight}"


class Language(models.Model):
    language = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.language} at {self.weight}"

class Skill(models.Model):
    skill = models.CharField(max_length=255)
    category = models.CharField(
        max_length=10, choices=[("hard", "Hard"), ("soft", "Soft")], default="hard"
    )
    weight = models.IntegerField(null=True)

    def __str__(self):
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
