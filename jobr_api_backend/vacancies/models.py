from django.db import models
from accounts.models import Employer, Employee
from accounts.models import CustomUser
from common.models import Language, ContractType, Function, Skill, Question

class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    contract_type = models.ForeignKey(ContractType, on_delete=models.CASCADE, blank=True, null=True)
    function = models.ForeignKey(Function, on_delete=models.CASCADE, blank=True, null=True)
    location = models.CharField(max_length=10,
                                choices=[('location', 'Location'), ('hybrid', 'Hybrid'), ('distance', 'Distance')],
                                default='location')
    skill = models.ManyToManyField(Skill)
    week_day = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    language = models.ManyToManyField(Language)
    question = models.ManyToManyField(Question)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # Latitude field
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # Longitude field

class ApplyVacancy(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)