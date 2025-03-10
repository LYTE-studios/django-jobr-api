from django.contrib.auth.models import AbstractUser
from django.db import models
from vacancies.models import Language, ContractType, Function, Skill


class ProfileOption(models.TextChoices):

    """
    An enumeration of profile types for users in the application.

    This class defines the available profile options for a user, which include:
    - Employee
    - Employer
    - Admin

    Each profile type has a database value.

    Attributes:
        EMPLOYEE (str): Represents an employee profile type with value 'employee'.
        EMPLOYER (str): Represents an employer profile type with value 'employer'.
        ADMIN (str): Represents an admin profile type with value 'admin'.
    """
    
    EMPLOYEE = "employee", "Employee"
    EMPLOYER = "employer", "Employer"
    ADMIN = "admin", "Admin"


class Employee(models.Model):
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        null=True
    )
    phone_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    city_name = models.CharField(max_length=100, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )  # Latitude field
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )  # Longitude field
    phone_session_counts = models.IntegerField(default=0)
    language = models.ManyToManyField(Language)
    contract_type = models.OneToOneField(
        ContractType, on_delete=models.CASCADE, blank=True, null=True
    )
    function = models.OneToOneField(
        Function, on_delete=models.CASCADE, blank=True, null=True
    )
    skill = models.ManyToManyField(Skill)

    def __str__(self):
        try:
            user = CustomUser.objects.get(employee_profile=self)
        except CustomUser.DoesNotExist:
            return "Not Found"

        return str(user)

class Employer(models.Model):
    vat_number = models.CharField(max_length=30, null=True)
    company_name = models.CharField(max_length=100, null=True)
    street_name = models.CharField(max_length=100, null=True)
    house_number = models.CharField(max_length=10, null=True)
    city = models.CharField(max_length=100, null=True)
    postal_code = models.CharField(max_length=20, null=True)
    coordinates = models.JSONField(null=True)
    website = models.URLField(blank=True, null=True)
    biography = models.TextField(blank=True, null=True)

    def __str__(self):
        try:
            user = CustomUser.objects.get(employer_profile=self)
        except CustomUser.DoesNotExist:
            return "Not Found"

        return str(user)

class Admin(models.Model):
    full_name = models.CharField(max_length=100)

    def __str__(self):
        try:
            user = CustomUser.objects.get(admin_profile=self)
        except CustomUser.DoesNotExist:
            return "Not Found"

        return str(user)


class Review(models.Model):
    REVIEWER_TYPE_CHOICES = [
        ("employee", "Employee"),
        ("employer", "Employer"),
        ("anonymous", "Anonymous"),  # For anonymous reviews
    ]
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="employee_reviews",
    )
    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="employer_reviews",
    )
    anonymous_name = models.CharField(max_length=100, blank=True, null=True)
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewer_type = models.CharField(
        max_length=10, choices=REVIEWER_TYPE_CHOICES, default="anonymous"
    )


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=10, choices=ProfileOption.choices, null=True, blank=True
    )

    employer_profile = models.OneToOneField(
        Employer, null=True, on_delete=models.CASCADE
    )
    employee_profile = models.OneToOneField(
        Employee, null=True, on_delete=models.CASCADE
    )

    admin_profile = models.OneToOneField(Admin, null=True, on_delete=models.CASCADE)

    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )

    def __str__(self) -> str:
        return f'{self.role} {self.email}'

    def save(self, *args, **kwargs):
        if self.role == ProfileOption.EMPLOYEE:
            self.employee_profile = Employee.objects.create()
        elif self.role == ProfileOption.EMPLOYER:
            self.employer_profile = Employer.objects.create()
        elif self.role == ProfileOption.ADMIN:
            self.admin_profile = Admin.objects.create()

        super().save(*args, **kwargs)

class UserGallery(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="user_gallery"
    )
    gallery = models.ImageField(upload_to="galleries/", blank=False)
