from PIL import Image
import io
from django.core.files.uploadedfile import SimpleUploadedFile

def create_test_image(filename='test.png'):
    """
    Create a test image file.
    """
    # Create a new image with a white background
    image = Image.new('RGB', (100, 100), 'white')
    
    # Save the image to a bytes buffer
    image_io = io.BytesIO()
    image.save(image_io, format='PNG')
    image_io.seek(0)
    
    # Create a SimpleUploadedFile
    return SimpleUploadedFile(
        filename,
        image_io.getvalue(),
        content_type='image/png'
    )