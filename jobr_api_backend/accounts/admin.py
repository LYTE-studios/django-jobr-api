from django.contrib import admin

# Register your models here.
from .models import Employee, Employer, Admin, Review, CustomUser

admin.site.register(CustomUser)
admin.site.register(Employee)
admin.site.register(Employer)
admin.site.register(Admin)
admin.site.register(Review)
