from django.db import models
from django.conf import settings

class Location(models.Model):
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.location


class ContractType(models.Model):
    contract_type = models.CharField(max_length=255)

    def __str__(self):
        return self.contract_type


class Function(models.Model):
    function = models.CharField(max_length=255)

    def __str__(self):
        return self.function


class Question(models.Model):
    question = models.CharField(max_length=255)

    def __str__(self):
        return self.question


class Language(models.Model):
    language = models.CharField(max_length=255)

    def __str__(self):
        return self.language


class Skill(models.Model):
    skill = models.CharField(max_length=255)
    category = models.CharField(max_length=10, choices=[('hard', 'Hard'), ('soft', 'Soft')], default='hard')

    def __str__(self):
        return self.skill

class MasteryOption(models.TextChoices):
    NONE = 'None'
    BEGINNER = 'Beginner'
    INTERMEDIATE = 'Intermediate'
    ADVANCED = 'Advanced'
    EXPERT = 'Expert'

class Weekday(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
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

    expected_mastery = models.CharField(max_length=255, choices=MasteryOption.choices, null=True)

    contract_type = models.ForeignKey(ContractType, on_delete=models.CASCADE, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    function = models.ForeignKey(Function, on_delete=models.CASCADE, blank=True, null=True)

    week_day = models.ManyToManyField(Weekday, null=True)
    job_date = models.DateField(null=True)

    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    languages = models.ManyToManyField(VacancyLanguage, related_name='vacancy_languages')

    descriptions = models.ManyToManyField(VacancyDescription)

    questions = models.ManyToManyField(VacancyQuestion)

    skill = models.ManyToManyField(Skill)

class ApplyVacancy(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)