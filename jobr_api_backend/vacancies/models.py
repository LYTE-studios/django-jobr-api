from django.db import models
from accounts.models import Employer, Employee
from common.models import Language, ContractType, Function, Skill, Question, Location

class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    contract_type = models.ForeignKey(ContractType, on_delete=models.CASCADE, blank=True, null=True)
    function = models.ForeignKey(Function, on_delete=models.CASCADE, blank=True, null=True)
    skill = models.ManyToManyField(Skill)
    week_day = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    language = models.ManyToManyField(Language)
    question = models.ManyToManyField(Question)
    location = models.ManyToManyField(Location)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # Latitude field
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # Longitude field

class ApplyVacancy(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)