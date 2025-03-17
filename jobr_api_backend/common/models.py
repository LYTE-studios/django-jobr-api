from django.db import models
from django.core.exceptions import ValidationError


class Extra(models.Model):
    """
    The `Extra` model is used to store additional information in the database. 
    It consists of a single field that can store a string of up to 255 characters.

    Fields:
    - `extra`: A `CharField` with a maximum length of 255 characters, storing extra information or items.
    
    Methods:
    - `__str__(self)`: Returns a string representation of the `Extra` instance, which is the value of the `extra` field.
    - `clean(self)`: Validates that the extra field is not empty or just whitespace.
    """
    extra = models.CharField(max_length=255)

    def clean(self):
        """
        Validates the extra field.
        
        Raises:
            ValidationError: If the extra field is empty or contains only whitespace.
        """
        if not self.extra or not self.extra.strip():
            raise ValidationError("Extra field cannot be empty or contain only whitespace.")

    def save(self, *args, **kwargs):
        """
        Overrides the save method to run full validation before saving.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a string representation of the `Extra` instance.
        
        This method returns the value of the `extra` field.

        Returns:
            str: The value of the `extra` field.
        """
        return self.extra
