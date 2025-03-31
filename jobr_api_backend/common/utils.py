from django.core.exceptions import ValidationError

def validate_image_size(value):
    """Validate that the uploaded image is not too large."""
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("The maximum file size that can be uploaded is 5MB")