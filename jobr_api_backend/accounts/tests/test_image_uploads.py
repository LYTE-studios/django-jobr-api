from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from ..models import CustomUser, UserGallery, ProfileOption
import os

class ImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test image file
        self.image_content = b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        self.test_image = SimpleUploadedFile(
            'test_image.gif',
            self.image_content,
            content_type='image/gif'
        )

    def test_upload_profile_picture(self):
        """Test uploading a profile picture."""
        url = reverse('profile-picture')
        data = {
            'image_type': 'profile_picture',
            'image': self.test_image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile_picture)
        self.assertTrue(os.path.exists(self.user.profile_picture.path))

    def test_delete_profile_picture(self):
        """Test deleting a profile picture."""
        # First upload a picture
        self.user.profile_picture = SimpleUploadedFile(
            'test_image.gif',
            self.image_content,
            content_type='image/gif'
        )
        self.user.save()
        picture_path = self.user.profile_picture.path

        # Then delete it
        url = reverse('profile-picture')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertFalse(self.user.profile_picture)
        self.assertFalse(os.path.exists(picture_path))

    def test_upload_profile_banner(self):
        """Test uploading a profile banner."""
        url = reverse('profile-banner')
        data = {
            'image_type': 'profile_banner',
            'image': self.test_image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile_banner)
        self.assertTrue(os.path.exists(self.user.profile_banner.path))

    def test_delete_profile_banner(self):
        """Test deleting a profile banner."""
        # First upload a banner
        self.user.profile_banner = SimpleUploadedFile(
            'test_image.gif',
            self.image_content,
            content_type='image/gif'
        )
        self.user.save()
        banner_path = self.user.profile_banner.path

        # Then delete it
        url = reverse('profile-banner')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertFalse(self.user.profile_banner)
        self.assertFalse(os.path.exists(banner_path))

    def test_add_gallery_image(self):
        """Test adding an image to the user's gallery."""
        url = reverse('profile-gallery-add')
        data = {
            'image': self.test_image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserGallery.objects.count(), 1)
        gallery_image = UserGallery.objects.first()
        self.assertTrue(os.path.exists(gallery_image.gallery.path))

    def test_delete_gallery_image(self):
        """Test deleting an image from the user's gallery."""
        # First add a gallery image
        gallery = UserGallery.objects.create(
            user=self.user,
            gallery=SimpleUploadedFile(
                'test_image.gif',
                self.image_content,
                content_type='image/gif'
            )
        )
        image_path = gallery.gallery.path

        # Then delete it
        url = reverse('profile-gallery-delete', args=[gallery.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UserGallery.objects.count(), 0)
        self.assertFalse(os.path.exists(image_path))

    def test_delete_other_users_gallery_image(self):
        """Test that a user cannot delete another user's gallery image."""
        # Create another user and their gallery image
        other_user = CustomUser.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        gallery = UserGallery.objects.create(
            user=other_user,
            gallery=SimpleUploadedFile(
                'test_image.gif',
                self.image_content,
                content_type='image/gif'
            )
        )

        # Try to delete it
        url = reverse('profile-gallery-delete', args=[gallery.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(UserGallery.objects.count(), 1)

    def tearDown(self):
        # Clean up any uploaded files
        if self.user.profile_picture:
            self.user.profile_picture.delete()
        if self.user.profile_banner:
            self.user.profile_banner.delete()
        for gallery in UserGallery.objects.all():
            gallery.gallery.delete()