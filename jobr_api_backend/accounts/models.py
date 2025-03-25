from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from vacancies.models import Language, ContractType, Function, Skill, Sector

def validate_image_size(value):
    """Validate that the uploaded image is not too large."""
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("The maximum file size that can be uploaded is 5MB")

class ProfileOption(models.TextChoices):
    """Profile types for users in the application."""
    EMPLOYEE = "employee", "Employee"
    EMPLOYER = "employer", "Employer"
    ADMIN = "admin", "Admin"

class Employee(models.Model):
    """Employee profile model."""
    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='employee_profile',
        null=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        null=True,
        blank=True
    )
    phone_number = models.CharField(max_length=15, null=True, blank=True, default=None)
    city_name = models.CharField(max_length=100, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone_session_counts = models.IntegerField(default=0)
    language = models.ManyToManyField(Language, blank=True)
    contract_type = models.OneToOneField(ContractType, on_delete=models.CASCADE, blank=True, null=True)
    function = models.OneToOneField(Function, on_delete=models.CASCADE, blank=True, null=True)
    skill = models.ManyToManyField(Skill, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.user.username if self.user else "Not Found"

class Employer(models.Model):
    """Employer profile model."""
    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='employer_profile',
        null=True
    )
    vat_number = models.CharField(max_length=30, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    street_name = models.CharField(max_length=100, null=True, blank=True)
    house_number = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    coordinates = models.JSONField(null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    biography = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username if self.user else "Not Found"

class Admin(models.Model):
    """Admin profile model."""
    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='admin_profile',
        null=True
    )
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username if self.user else "Not Found"

class CustomUser(AbstractUser):
    """Custom user model with role-based profiles."""
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=ProfileOption.choices,
        null=True,
        blank=True
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text="The business sector this user belongs to"
    )
    is_blocked = models.BooleanField(
        default=False,
        help_text="Designates whether this user is blocked from accessing the platform."
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ],
        help_text="User's profile picture (max 5MB, jpg, jpeg, png, gif)"
    )
    profile_banner = models.ImageField(
        upload_to="profile_banners/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ],
        help_text="User's profile banner image (max 5MB, jpg, jpeg, png, gif)"
    )

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Handle profile creation/updates on save."""
        is_new = self.pk is None
        old_role = None if is_new else CustomUser.objects.get(pk=self.pk).role

        # Save the user first
        super().save(*args, **kwargs)

        # Handle profile creation/updates
        if is_new or old_role != self.role:
            # Delete old profile if role changed
            if not is_new:
                if old_role == ProfileOption.EMPLOYEE:
                    if hasattr(self, 'employee_profile') and self.employee_profile:
                        self.employee_profile.delete()
                        self.employee_profile = None
                elif old_role == ProfileOption.EMPLOYER:
                    if hasattr(self, 'employer_profile') and self.employer_profile:
                        self.employer_profile.delete()
                        self.employer_profile = None
                elif old_role == ProfileOption.ADMIN:
                    if hasattr(self, 'admin_profile') and self.admin_profile:
                        self.admin_profile.delete()
                        self.admin_profile = None

            # Create new profile based on role
            if self.role == ProfileOption.EMPLOYEE:
                Employee.objects.create(user=self)
            elif self.role == ProfileOption.EMPLOYER:
                Employer.objects.create(user=self)
            elif self.role == ProfileOption.ADMIN:
                Admin.objects.create(user=self)

    class Meta:
        ordering = ['id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

class UserGallery(models.Model):
    """User gallery for uploading images."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_gallery"
    )
    gallery = models.ImageField(upload_to="galleries/", blank=False)

    def __str__(self):
        return f"Gallery image for {self.user.username}"

class LikedEmployee(models.Model):
    """Represents an employee that has been liked by an employer."""
    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name='liked_employees'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='liked_by_employers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employer', 'employee')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employer} likes {self.employee}"

class Review(models.Model):
    """
    Represents a review given by an employer to an employee or vice versa.
    """
    reviewer = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    reviewed = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('reviewer', 'reviewed')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.reviewer} for {self.reviewed}"

    def clean(self):
        if self.reviewer == self.reviewed:
            raise ValidationError("Users cannot review themselves")
        if self.reviewer.role == self.reviewed.role:
            raise ValidationError("Users can only review users of different roles")

class VATValidationResult(models.Model):
    """Stores VAT validation results."""
    vat_number = models.CharField(max_length=20, unique=True)
    is_valid = models.BooleanField()
    company_name = models.CharField(max_length=255, blank=True)
    company_address = models.TextField(blank=True)
    validation_date = models.DateTimeField(auto_now_add=True)
    employer = models.ForeignKey(
        Employer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vat_validations'
    )

    class Meta:
        ordering = ['-validation_date']
        verbose_name = 'VAT Validation Result'
        verbose_name_plural = 'VAT Validation Results'

    def __str__(self):
        return f"{self.vat_number} - {'Valid' if self.is_valid else 'Invalid'}"
