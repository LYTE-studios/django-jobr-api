from django.db import models
from accounts.models import CustomUser


# Create your models here.
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


class Extra(models.Model):
    extra = models.CharField(max_length=255)

    def __str__(self):
        return self.extra


class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    contract_type = models.OneToOneField(ContractType, on_delete=models.CASCADE, blank=True, null=True)
    function = models.OneToOneField(Function, on_delete=models.CASCADE, blank=True, null=True)
    location = models.CharField(max_length=10,
                                choices=[('location', 'Location'), ('hybrid', 'Hybrid'), ('distance', 'Distance')],
                                default='location')
    skill = models.ManyToManyField(Skill, blank=True, null=True)
    week_day = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    language = models.ManyToManyField(Language, blank=True, null=True)
    question = models.ManyToManyField(Question, blank=True, null=True)


class ApplyVacancy(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    vacancy = models.OneToOneField(Vacancy, on_delete=models.CASCADE)
