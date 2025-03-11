from django.contrib import admin


## REMOVE UNWANTED MODELS FROM ADMIN

from django.contrib.auth.models import Group
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

# Unregister models you don't want in admin
admin.site.unregister(Group)
admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)

## END REMOVE

# Register your models here.
from .models import Review, CustomUser, Employee, Employer

admin.site.register(CustomUser)
admin.site.register(Review)
admin.site.register(Employer)   
admin.site.register(Employee)
