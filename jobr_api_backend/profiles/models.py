from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import json

class Education(models.Model):
    """
    Represents an educational qualification of an employee.
    """
    employee = models.ForeignKey('accounts.Employee', on_delete=models.CASCADE, related_name='education_set')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_ongoing = models.BooleanField(default=False)
    grade = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(4.0)]
    )
    _achievements = models.TextField(db_column='achievements', blank=True, default='[]')
    description = models.TextField()
    certificate_url = models.URLField(null=True, blank=True)
    institution_logo_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def achievements(self):
        return json.loads(self._achievements)

    @achievements.setter
    def achievements(self, value):
        self._achievements = json.dumps(value)

    class Meta:
        ordering = ['-end_date', '-start_date']
        verbose_name = 'Education'
        verbose_name_plural = 'Education'

    def __str__(self):
        return f"{self.degree} in {self.field_of_study} at {self.institution}"

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")
        
        if self.is_ongoing and self.end_date:
            raise ValidationError("Ongoing education cannot have an end date.")
        
        if not self.is_ongoing and not self.end_date:
            raise ValidationError("Non-ongoing education must have an end date.")

        if self.start_date and self.start_date > timezone.now().date():
            raise ValidationError("Start date cannot be in the future.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class WorkExperience(models.Model):
    """
    Represents a work experience entry of an employee.
    """
    employee = models.ForeignKey('accounts.Employee', on_delete=models.CASCADE, related_name='work_experience_set')
    company_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current_position = models.BooleanField(default=False)
    _responsibilities = models.TextField(db_column='responsibilities', blank=True, default='[]')
    _achievements = models.TextField(db_column='achievements', blank=True, default='[]')
    company_logo_url = models.URLField(null=True, blank=True)
    company_website = models.URLField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def responsibilities(self):
        return json.loads(self._responsibilities)

    @responsibilities.setter
    def responsibilities(self, value):
        self._responsibilities = json.dumps(value)

    @property
    def achievements(self):
        return json.loads(self._achievements)

    @achievements.setter
    def achievements(self, value):
        self._achievements = json.dumps(value)

    class Meta:
        ordering = ['-end_date', '-start_date']
        verbose_name = 'Work Experience'
        verbose_name_plural = 'Work Experience'

    def __str__(self):
        return f"{self.position} at {self.company_name}"

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")
        
        if self.is_current_position and self.end_date:
            raise ValidationError("Current position cannot have an end date.")
        
        if not self.is_current_position and not self.end_date:
            raise ValidationError("Past position must have an end date.")

        if self.start_date and self.start_date > timezone.now().date():
            raise ValidationError("Start date cannot be in the future.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class PortfolioItem(models.Model):
    """
    Represents a portfolio item of an employee.
    """
    employee = models.ForeignKey('accounts.Employee', on_delete=models.CASCADE, related_name='portfolio_set')
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField(null=True, blank=True)
    _images = models.TextField(db_column='images', blank=True, default='[]')
    date = models.DateField()
    video_url = models.URLField(null=True, blank=True)
    github_url = models.URLField(null=True, blank=True)
    _collaborators = models.TextField(db_column='collaborators', blank=True, default='[]')
    client_name = models.CharField(max_length=255, null=True, blank=True)
    client_testimonial = models.TextField(null=True, blank=True)
    client_rating = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    _tags = models.TextField(db_column='tags', blank=True, default='[]')
    is_public = models.BooleanField(default=True)
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def images(self):
        return json.loads(self._images)

    @images.setter
    def images(self, value):
        self._images = json.dumps(value)

    @property
    def collaborators(self):
        return json.loads(self._collaborators)

    @collaborators.setter
    def collaborators(self, value):
        self._collaborators = json.dumps(value)

    @property
    def tags(self):
        return json.loads(self._tags)

    @tags.setter
    def tags(self, value):
        self._tags = json.dumps(value)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Portfolio Item'
        verbose_name_plural = 'Portfolio Items'

    def __str__(self):
        return self.title

    def clean(self):
        if self.date and self.date > timezone.now().date():
            raise ValidationError("Date cannot be in the future.")

        if self.client_rating and (self.client_rating < 0 or self.client_rating > 5):
            raise ValidationError("Client rating must be between 0 and 5.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
