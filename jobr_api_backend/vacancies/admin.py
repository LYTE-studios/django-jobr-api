from django.contrib import admin

# Register your models here
from .models import Vacancy, Question, ContractType, Function, Language, Skill, Location, Weekday

admin.site.register(Vacancy)
admin.site.register(Question)
admin.site.register(ContractType)   
admin.site.register(Function)
admin.site.register(Language)
admin.site.register(Skill)
admin.site.register(Location)
admin.site.register(Weekday)