from django.test import TestCase
from django.core.exceptions import ValidationError
from common.models import Extra

class ExtraModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for Extra model tests
        """
        self.extra_data = "Test extra data"
        self.extra = Extra.objects.create(extra=self.extra_data)

    def test_extra_creation(self):
        """
        Test creating an Extra instance with valid data
        """
        self.assertEqual(self.extra.extra, self.extra_data)
        self.assertTrue(isinstance(self.extra, Extra))

    def test_extra_string_representation(self):
        """
        Test the string representation of an Extra instance
        """
        self.assertEqual(str(self.extra), self.extra_data)

    def test_extra_max_length(self):
        """
        Test that Extra.extra field respects max_length
        """
        max_length = 255
        # Create string that exceeds max_length
        long_string = "x" * (max_length + 1)
        
        # Attempt to create Extra with too long string should raise an error
        with self.assertRaises(ValidationError):
            extra = Extra(extra=long_string)
            extra.full_clean()
        
        # String at max_length should work
        valid_string = "x" * max_length
        extra = Extra(extra=valid_string)
        extra.full_clean()  # Should not raise an error
        extra.save()
        self.assertEqual(len(extra.extra), max_length)

    def test_extra_blank_value(self):
        """
        Test that Extra.extra field cannot be blank
        """
        # Test empty string
        with self.assertRaises(ValidationError):
            extra = Extra(extra="")
            extra.full_clean()

        # Test whitespace only
        with self.assertRaises(ValidationError):
            extra = Extra(extra="   ")
            extra.full_clean()

    def test_extra_update(self):
        """
        Test updating an Extra instance
        """
        new_value = "Updated extra data"
        self.extra.extra = new_value
        self.extra.save()
        
        # Refresh from database
        self.extra.refresh_from_db()
        self.assertEqual(self.extra.extra, new_value)

    def test_extra_delete(self):
        """
        Test deleting an Extra instance
        """
        extra_id = self.extra.id
        self.extra.delete()
        
        # Verify the instance was deleted
        with self.assertRaises(Extra.DoesNotExist):
            Extra.objects.get(id=extra_id)

    def test_multiple_extras(self):
        """
        Test creating multiple Extra instances
        """
        extra2 = Extra.objects.create(extra="Second extra")
        extra3 = Extra.objects.create(extra="Third extra")
        
        # Verify all instances exist
        self.assertEqual(Extra.objects.count(), 3)
        
        # Verify each instance has correct data
        extras = Extra.objects.all().order_by('id')
        self.assertEqual(extras[0].extra, self.extra_data)
        self.assertEqual(extras[1].extra, "Second extra")
        self.assertEqual(extras[2].extra, "Third extra")

    def test_extra_validation_on_save(self):
        """
        Test that validation is performed on save
        """
        # Test empty string
        with self.assertRaises(ValidationError):
            Extra.objects.create(extra="")

        # Test whitespace only
        with self.assertRaises(ValidationError):
            Extra.objects.create(extra="   ")

        # Test string exceeding max_length
        with self.assertRaises(ValidationError):
            Extra.objects.create(extra="x" * 256)