from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class BaseModel(models.Model):
    """
    Base model with common fields and documentation.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    @classmethod
    def get_field_help_texts(cls):
        """
        Get help texts for model fields.
        """
        return {
            field.name: field.help_text
            for field in cls._meta.fields
            if hasattr(field, 'help_text') and field.help_text
        }

    @classmethod
    def get_required_fields(cls):
        """
        Get list of required fields.
        """
        return [
            field.name
            for field in cls._meta.fields
            if not field.blank and not field.auto_created
        ]

    @classmethod
    def get_field_choices(cls):
        """
        Get choices for fields that have them.
        """
        return {
            field.name: field.choices
            for field in cls._meta.fields
            if hasattr(field, 'choices') and field.choices
        }

    @classmethod
    def get_field_validators(cls):
        """
        Get validators for fields that have them.
        """
        validators = {}
        for field in cls._meta.fields:
            if hasattr(field, 'validators') and field.validators:
                validators[field.name] = [
                    {
                        'name': validator.__class__.__name__,
                        'description': str(validator)
                    }
                    for validator in field.validators
                ]
        return validators

    @classmethod
    def get_model_documentation(cls):
        """
        Get comprehensive model documentation.
        """
        return {
            'name': cls.__name__,
            'description': cls.__doc__,
            'help_texts': cls.get_field_help_texts(),
            'required_fields': cls.get_required_fields(),
            'choices': cls.get_field_choices(),
            'validators': cls.get_field_validators(),
            'ordering': cls._meta.ordering,
            'abstract': cls._meta.abstract,
            'app_label': cls._meta.app_label,
            'model_name': cls._meta.model_name,
        }

    def __str__(self):
        """
        Default string representation.
        """
        return f"{self.__class__.__name__} {self.id}"

class BaseModelWithMetadata(BaseModel):
    """
    Base model with metadata fields.
    """
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional metadata stored as JSON"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Additional notes or comments"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this record is active"
    )

    class Meta:
        abstract = True

class Extra(models.Model):
    """
    Extra model for storing additional data
    """
    extra = models.CharField(
        max_length=255,
        help_text="Additional data"
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )
    updated_at = models.DateTimeField(
        default=timezone.now
    )

    def __str__(self):
        return self.extra

    def clean(self):
        if not self.extra or self.extra.isspace():
            raise ValidationError("Extra field cannot be empty or whitespace only")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
