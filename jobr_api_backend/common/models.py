from django.db import models


class Extra(models.Model):
    """
    The `Extra` model is used to store additional information in the database. 
    It consists of a single field that can store a string of up to 255 characters.

    Fields:
    - `extra`: A `CharField` with a maximum length of 255 characters, storing extra information or items.
    
    Methods:
    - `__str__(self)`: Returns a string representation of the `Extra` instance, which is the value of the `extra` field.
    """
    extra = models.CharField(max_length=255)

    def __str__(self):

        """
        Returns a string representation of the `Extra` instance.
        
        This method returns the value of the `extra` field.

        Returns:
            str: The value of the `extra` field.
        """
        return self.extra
