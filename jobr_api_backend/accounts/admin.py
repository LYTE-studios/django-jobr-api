from django.contrib import admin

# Register your models here.
from .models import Employee, Employer, Admin

admin.site.register(Employee)
admin.site.register(Employer)
admin.site.register(Admin)
