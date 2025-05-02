from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from vacancies.models import Language, ContractType, Function, Skill, Sector

from common.utils import validate_image_size

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
    phone_session_counts = models.IntegerField(default=0)
    availability_status = models.CharField(
        max_length=20,
        choices=[
            ('immediately', 'Immediately Available'),
            ('two_weeks', 'Available in 2 Weeks'),
            ('one_month', 'Available in 1 Month'),
            ('three_months', 'Available in 3 Months'),
            ('unavailable', 'Not Available')
        ],
        default='immediately',
        help_text="Employee's current availability status"
    )
    availability_date = models.DateField(
        null=True,
        blank=True,
        help_text="Specific date when the employee will be available"
    )
    experience_description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of work experience"
    )
    employment_type = models.CharField(
        max_length=20,
        choices=[
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('contract', 'Contract'),
            ('temporary', 'Temporary'),
            ('internship', 'Internship')
        ],
        null=True,
        blank=True,
        help_text="Preferred type of employment"
    )
    language = models.ManyToManyField(
        Language,
        through='EmployeeLanguage',
        blank=True,
        related_name='employees'
    )
    contract_type = models.OneToOneField(ContractType, on_delete=models.CASCADE, blank=True, null=True)
    function = models.OneToOneField(Function, on_delete=models.CASCADE, blank=True, null=True)
    skill = models.ManyToManyField(Skill, blank=True)
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

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.user.username if self.user else "Not Found"

class Company(models.Model):
    """Company model that can have multiple users."""
    name = models.CharField(max_length=100)
    vat_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    street_name = models.CharField(max_length=100, null=True, blank=True)
    house_number = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True, help_text="Link to company's Instagram profile")
    tiktok_url = models.URLField(blank=True, null=True, help_text="Link to company's TikTok profile")
    facebook_url = models.URLField(blank=True, null=True, help_text="Link to company's Facebook profile")
    description = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    employee_count = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Number of employees in the company (e.g., '1-10', '11-50', '51-200', etc.)"
    )

    def save(self, *args, **kwargs):
        """Override save to set VAT number from first company if not set."""
        if not self.vat_number and not self.pk:  # Only for new companies without VAT
            # Get all users who will be owners of this company
            company_users = kwargs.pop('company_users', [])
            for user in company_users:
                if user.role == ProfileOption.EMPLOYER:
                    # Get the first company's VAT number
                    first_company = user.companies.order_by('created_at').first()
                    if first_company and first_company.vat_number:
                        self.vat_number = first_company.vat_number
                        break
        
        super().save(*args, **kwargs)
    users = models.ManyToManyField(
        'CustomUser',
        through='CompanyUser',
        related_name='companies'
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sector',
        help_text="The business sector this user belongs to"
    )
    profile_picture = models.ImageField(
        upload_to="company_profile_pictures/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ],
        help_text="Company's profile picture (max 5MB, jpg, jpeg, png, gif)"
    )
    profile_banner = models.ImageField(
        upload_to="company_profile_banners/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ],
        help_text="Company's profile banner image (max 5MB, jpg, jpeg, png, gif)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        return self.name

class CompanyUser(models.Model):
    """Through model for Company-User relationship with role."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[
            ('owner', 'Owner'),
            ('admin', 'Administrator'),
            ('member', 'Member')
        ],
        default='member'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'user')
        verbose_name = 'Company User'
        verbose_name_plural = 'Company Users'

    def __str__(self):
        return f"{self.user.username} - {self.company.name} ({self.role})"

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
    selected_company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='selected_by_users',
        help_text="The currently selected company for this user"
    )
    is_blocked = models.BooleanField(
        default=False,
        help_text="Designates whether this user is blocked from accessing the platform."
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
                elif old_role == ProfileOption.ADMIN:
                    if hasattr(self, 'admin_profile') and self.admin_profile:
                        self.admin_profile.delete()
                        self.admin_profile = None

            # Create new profile based on role
            if self.role == ProfileOption.EMPLOYEE:
                Employee.objects.get_or_create(user=self)
            elif self.role == ProfileOption.EMPLOYER:
                # Create a default company for new employer users
                if is_new:
                    with transaction.atomic():
                        # Get VAT number from first company if it exists
                        from .services import CompanyService
                        vat_number = CompanyService.get_first_company_vat_number(self)
                        
                        company = Company(
                            name=f"{self.username}'s Company",
                            street_name="",
                            house_number="",
                            city="",
                            postal_code=""
                        )
                        company.save(company_users=[self])
                        CompanyUser.objects.create(
                            company=company,
                            user=self,
                            role='owner'
                        )
                        self.selected_company = company
                        self.save(update_fields=['selected_company'])
                else:
                    # For existing employer users without a selected company,
                    # set it to their first company if they have any
                    if not self.selected_company and self.companies.exists():
                        self.selected_company = self.companies.first()
                        self.save(update_fields=['selected_company'])
            elif self.role == ProfileOption.ADMIN:
                Admin.objects.create(user=self)

    class Meta:
        ordering = ['id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

class EmployeeLanguage(models.Model):
    """Through model for Employee-Language relationship with mastery level."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    mastery = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('native', 'Native')
        ],
        default='beginner'
    )

    class Meta:
        unique_together = ('employee', 'language')
        verbose_name = 'Employee Language'
        verbose_name_plural = 'Employee Languages'
        ordering = ['id']

    def __str__(self):
        return f"{self.employee.user.username} - {self.language.name} ({self.mastery})"

class CompanyGallery(models.Model):
    """Company gallery for uploading images."""
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="company_gallery"
    )
    gallery = models.ImageField(
        upload_to="company_galleries/",
        blank=False,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ],
        help_text="Company gallery image (max 5MB, jpg, jpeg, png, gif)"
    )

    class Meta:
        verbose_name = 'Company Gallery'
        verbose_name_plural = 'Company Galleries'
        ordering = ['id']

    def __str__(self):
        return f"Gallery image for {self.company.name}"

class LikedEmployee(models.Model):
    """Represents an employee that has been liked by a company."""
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='liked_employees',
        null=True
    )
    liked_by = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='liked_employees_as_user',
        null=True
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='liked_by_companies'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'employee')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company.name} (by {self.liked_by.username}) likes {self.employee}"

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
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vat_validations'
    )
    validated_by = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vat_validations_performed'
    )

    class Meta:
        ordering = ['-validation_date']
        verbose_name = 'VAT Validation Result'
        verbose_name_plural = 'VAT Validation Results'

    def __str__(self):
        return f"{self.vat_number} - {'Valid' if self.is_valid else 'Invalid'}"

class EmployeeGallery(models.Model):
    """Employee gallery for uploading images."""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="employee_gallery"
    )
    gallery = models.ImageField(
        upload_to="employee_galleries/",
        blank=False,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ],
        help_text="Employee gallery image (max 5MB, jpg, jpeg, png, gif)"
    )

    class Meta:
        verbose_name = 'Employee Gallery'
        verbose_name_plural = 'Employee Galleries'
        ordering = ['id']

    def __str__(self):
        return f"Gallery image for {self.employee.user.username}"

class EmployeeGallery(models.Model):
    """Employee gallery for uploading images."""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="employee_gallery"
    )
    gallery = models.ImageField(
        upload_to="employee_galleries/",
        blank=False,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ],
        help_text="Employee gallery image (max 5MB, jpg, jpeg, png, gif)"
    )

    class Meta:
        verbose_name = 'Employee Gallery'
        verbose_name_plural = 'Employee Galleries'
        ordering = ['id']

    def __str__(self):
        return f"Gallery image for {self.employee.user.username}"
