from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Employee
from vacancies.models import Vacancy


class AISuggestion(models.Model):
    """
    Model for AI-generated suggestions matching employees with vacancies.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='ai_suggestions'
    )
    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name='ai_suggestions'
    )
    quantitative_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Score based on quantitative data (0-100)'
    )
    qualitative_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Score based on qualitative data from LLM (0-100)'
    )
    total_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Combined score from quantitative and qualitative analysis'
    )
    message = models.TextField(
        help_text='Explanation from the LLM about why this match was suggested'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_score', '-created_at']
        verbose_name = 'AI Suggestion'
        verbose_name_plural = 'AI Suggestions'
        unique_together = ['employee', 'vacancy']

    def __str__(self):
        return f'Match: {self.employee} - {self.vacancy} (Score: {self.total_score})'


class SuggestionWeight(models.Model):
    """
    Model for configuring weights used in the suggestion algorithm.
    """
    FIELD_CHOICES = [
        ('distance', 'Distance'),
        ('availability', 'Availability'),
        ('languages', 'Languages'),
        ('functions', 'Functions'),
        ('hard_skills', 'Hard Skills'),
        ('soft_skills', 'Soft Skills'),
        ('biography', 'Biography'),
        ('company_bio', 'Company Biography'),
        ('education', 'Education'),
        ('interests', 'Interests'),
        ('description', 'Vacancy Description'),
        ('questions', 'Vacancy Questions'),
    ]

    MASTERY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    FIELD_TYPE_CHOICES = [
        ('quantitative', 'Quantitative'),
        ('qualitative', 'Qualitative'),
    ]

    name = models.CharField(
        max_length=50,
        choices=FIELD_CHOICES,
        help_text='The field this weight applies to'
    )
    weight = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Weight percentage (0-100)'
    )
    mastery_level = models.CharField(
        max_length=20,
        choices=MASTERY_CHOICES,
        null=True,
        blank=True,
        help_text='If set, this weight only applies to vacancies with this mastery level'
    )
    field_type = models.CharField(
        max_length=20,
        choices=FIELD_TYPE_CHOICES,
        help_text='Whether this weight applies to quantitative or qualitative scoring'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Suggestion Weight'
        verbose_name_plural = 'Suggestion Weights'
        unique_together = ['name', 'mastery_level']

    def __str__(self):
        if self.mastery_level:
            return f'{self.name} ({self.mastery_level}): {int(self.weight)}%'
        return f'{self.name}: {int(self.weight)}%'


class SuggestionGenerationLog(models.Model):
    """
    Model for logging suggestion generation runs.
    """
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    suggestions_created = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    is_successful = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Suggestion Generation Log'
        verbose_name_plural = 'Suggestion Generation Logs'

    def __str__(self):
        status = 'Successful' if self.is_successful else 'Failed'
        return f'Generation on {self.started_at.date()} - {status}'
