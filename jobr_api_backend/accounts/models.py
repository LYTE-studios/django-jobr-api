from django.contrib.auth.models import AbstractUser
from django.db import models
from vacancies.models import Language, ContractType, Function, Skill
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

def validate_image_size(value):
    """
    Validate that the uploaded image is not too large.
    
    Args:
        value (File): The uploaded image file.
    
    Raises:
        ValidationError: If the file is larger than 5MB.
    """
    filesize = value.size
    
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("The maximum file size that can be uploaded is 5MB")


class ProfileOption(models.TextChoices):
    """
    An enumeration of profile types for users in the application.

    This class defines the available profile options for a user, which include:
    - Employee
    - Employer
    - Admin

    Each profile type has a database value.
    """
    
    EMPLOYEE = "employee", "Employee"
    EMPLOYER = "employer", "Employer"
    ADMIN = "admin", "Admin"


class Employee(models.Model):
    """ Represents an employee's profile with personal, contact, and work-related information.

    Methods:
        __str__(self): Returns the string representation of the employee's associated user if exists.

    """
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        null=True,
        blank=True
    )
    phone_number = models.CharField(max_length=15, null=True, blank=True, default=None)  # Made nullable, blank, and default None
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
    language = models.ManyToManyField(Language, blank=True)  # Made blank=True
    contract_type = models.OneToOneField(
        ContractType, on_delete=models.CASCADE, blank=True, null=True
    )
    function = models.OneToOneField(
        Function, on_delete=models.CASCADE, blank=True, null=True
    )
    skill = models.ManyToManyField(Skill, blank=True)  # Made blank=True

    def __str__(self):
        try:
            user = CustomUser.objects.get(employee_profile=self)
            return user.username
        except CustomUser.DoesNotExist:
            return "Not Found"


class Employer(models.Model):
    """ Represents an employer's profile with personal, contact, and work-related information.

    Methods:
        __str__(self): Returns the string representation of the employer's associated user if exists.

    """

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
        try:
            user = CustomUser.objects.get(employer_profile=self)
            return user.username
        except CustomUser.DoesNotExist:
            return "Not Found"


class Admin(models.Model):
    """ Represents the admin's profile with their full-name.

    Attributes:
        full_name (str): The full name of the admin.

    Methods:
        __str__(self): Returns the string representation of the admin's associated user if exists.

    """

    full_name = models.CharField(max_length=100)

    def __str__(self):
        try:
            user = CustomUser.objects.get(admin_profile=self)
            return user.username
        except CustomUser.DoesNotExist:
            return "Not Found"


class Review(models.Model):
    """
    Represents a review given by either an employee, employer, or anonymously.

    Attributes:
        employee (ForeignKey): A reference to the Employee associated with the review, if applicable.
        employer (ForeignKey): A reference to the Employer associated with the review, if applicable.
        anonymous_name (str): The name of the reviewer if the review is anonymous.
        rating (int): The rating given in the review, typically on a scale of 1 to 5.
        comment (str): The comment provided in the review.
        created_at (datetime): The timestamp when the review was created.
        reviewer_type (str): Indicates the type of reviewer (employee, employer, or anonymous).

    """

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
    """
    Custom user model extending the AbstractUser class to include additional fields 
    specific to the application's use case.

    Attributes:
        email (str): The email address of the user, which must be unique.
        role (str): The role of the user, selected from predefined profile options 
                    (employee, employer, or admin).
        employer_profile (Employer): A one-to-one relationship with the Employer 
                                     profile, if the user is an employer.
        employee_profile (Employee): A one-to-one relationship with the Employee 
                                     profile, if the user is an employee.
        admin_profile (Admin): A one-to-one relationship with the Admin profile, 
                               if the user is an admin.
        profile_picture (Image): An optional field for the user's profile picture.
        profile_banner (Image): An optional field for the user's profile banner.

    Methods:
        __str__(self): Returns a string representation of the user, consisting of 
                       their role and email.
        save(self, *args, **kwargs): Overridden save method to automatically create 
                                     related profiles based on the user's role.
    """

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=10, 
        choices=ProfileOption.choices, 
        null=True, 
        blank=True
    )

    employer_profile = models.OneToOneField(
        Employer, null=True, on_delete=models.CASCADE
    )
    employee_profile = models.OneToOneField(
        Employee, null=True, on_delete=models.CASCADE
    )
    admin_profile = models.OneToOneField(
        Admin, null=True, on_delete=models.CASCADE
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

    def save(self, *args, **kwargs):
        """
        Overridden save method to automatically create related profiles 
        based on the user's role.

        Creates an employee, employer, or admin profile if it does not already exist.
        """
        if self.role == ProfileOption.EMPLOYEE and not self.employee_profile:
            self.employee_profile = Employee.objects.create(phone_number=None)  # Explicitly set phone_number to None
        elif self.role == ProfileOption.EMPLOYER and not self.employer_profile:
            self.employer_profile = Employer.objects.create()
        elif self.role == ProfileOption.ADMIN and not self.admin_profile:
            self.admin_profile = Admin.objects.create()

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Returns a string representation of the CustomUser instance.

        Returns:
            str: A string representation of the user's username.
        """
        return self.username


class UserGallery(models.Model):
    """
    Represents a gallery for a user, where the user can upload images.

    Attributes:
        user (CustomUser): A foreign key to the CustomUser model, representing the user who owns the gallery.
        gallery (Image): The image file uploaded by the user.

    """
      
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="user_gallery"
    )
    gallery = models.ImageField(upload_to="galleries/", blank=False)
