from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import CustomUser, Employee, Employer, ProfileOption
from django.conf import settings
from .test_utils import create_test_image
import os

class UserRegistrationTests(APITestCase):
    def setUp(self):
        """
        Set up test data for registration tests
        """
        self.registration_url = reverse('user-registration')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'role': ProfileOption.EMPLOYEE
        }

    def test_user_registration_success(self):
        """
        Test successful user registration
        """
        response = self.client.post(self.registration_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_registration_duplicate_username(self):
        """
        Test registration with duplicate username
        """
        # Create first user
        self.client.post(self.registration_url, self.user_data, format='json')
        
        # Try to create second user with same username
        response = self.client.post(self.registration_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserLoginTests(APITestCase):
    def setUp(self):
        """
        Set up test data for login tests
        """
        self.login_url = reverse('user-login')
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )

    def test_user_login_success(self):
        """
        Test successful user login
        """
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class UserProfileTests(APITestCase):
    def setUp(self):
        """
        Set up test data for profile tests
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.profile_url = reverse('my-profile')

    def test_get_my_profile(self):
        """
        Test retrieving user's own profile
        """
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_update_my_profile(self):
        """
        Test updating user profile
        """
        data = {
            'username': 'updateduser',
            'email': 'updated@example.com'
        }
        response = self.client.put(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'updateduser')
        self.assertEqual(response.data['email'], 'updated@example.com')

class ProfileImageUploadTests(APITestCase):
    def setUp(self):
        """
        Set up test data for image upload tests
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.upload_url = reverse('profile-image-upload')
        self.image = create_test_image()

    def test_upload_profile_picture(self):
        """
        Test uploading a profile picture
        """
        data = {
            'image_type': 'profile_picture',
            'image': self.image
        }
        response = self.client.put(
            self.upload_url,
            data,
            format='multipart'
        )
        if response.status_code != status.HTTP_200_OK:
            print("Response data:", response.data)  # Debug line
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image_url', response.data)

    def test_upload_profile_banner(self):
        """
        Test uploading a profile banner
        """
        data = {
            'image_type': 'profile_banner',
            'image': self.image
        }
        response = self.client.put(
            self.upload_url,
            data,
            format='multipart'
        )
        if response.status_code != status.HTTP_200_OK:
            print("Response data:", response.data)  # Debug line
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image_url', response.data)

    def test_delete_profile_picture(self):
        """
        Test deleting a profile picture
        """
        response = self.client.delete(f"{self.upload_url}?image_type=profile_picture")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_profile_banner(self):
        """
        Test deleting a profile banner
        """
        response = self.client.delete(f"{self.upload_url}?image_type=profile_banner")
        self.assertEqual(response.status_code, status.HTTP_200_OK)