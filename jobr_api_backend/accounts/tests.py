from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser, Employee, Employer, ProfileOption

from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch
from datetime import date

User = get_user_model()

class UserTests(APITestCase):
    def setUp(self):
        # Create a test user with multiple profiles
        self.user = CustomUser.objects.create_user(
            username="testuser", 
            email="test@example.com", 
            password="testpass",
            role=ProfileOption.EMPLOYEE
        )
        
        # Refresh the user to ensure the employee_profile is created
        self.user.refresh_from_db()

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

    def test_user_registration_cycle(self):
        """
        Test the complete user registration process
        """
        register_url = reverse("register")
        register_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "role": ProfileOption.EMPLOYEE,
        }
        register_response = self.client.post(register_url, register_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("access" in register_response.data)
        self.assertTrue("refresh" in register_response.data)

    def test_login_authentication(self):
        """
        Test user login and token generation
        """
        login_url = reverse("login")
        login_data = {"username": "testuser", "password": "testpass"}
        login_response = self.client.post(login_url, login_data)
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in login_response.data)
        self.assertTrue("refresh" in login_response.data)

    def test_token_refresh(self):
        """
        Test token refresh mechanism
        """
        # First login to get refresh token
        login_url = reverse("login")
        login_response = self.client.post(
            login_url, {"username": "testuser", "password": "testpass"}
        )
        
        # Extract refresh token
        refresh_token = login_response.data.get("refresh")
        self.assertIsNotNone(refresh_token, "No refresh token in response")

        # Try refresh
        refresh_url = reverse("token_refresh")
        refresh_response = self.client.post(refresh_url, {"refresh": refresh_token})
        
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(refresh_response.data.get("access"))

    def test_user_get_full_profile(self):
        """
        Test retrieving a user's full profile with all associated data
        """
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user details
        self.assertEqual(response.data['username'], "testuser")
        self.assertEqual(response.data['email'], "test@example.com")

    def test_user_full_profile_update(self):
        """
        Test updating user, employer, and employee profiles in a single request
        """
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        
        update_data = {
            "username": "updateduser",
            "email": "updated@example.com",
            "employee_profile": {
                "date_of_birth": "1995-05-05",
                "gender": "female",
                "phone_number": "0987654321",
                "city_name": "Updated City",
                "biography": "Updated biography"
            }
        }

        response = self.client.put(url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh user from database
        self.user.refresh_from_db()

        # Verify user fields updated
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.email, "updated@example.com")
        employee_profile = self.user.employee_profile
        self.assertEqual(str(employee_profile.date_of_birth), "1995-05-05")
        self.assertEqual(employee_profile.gender, "female")
        self.assertEqual(employee_profile.phone_number, "0987654321")
        self.assertEqual(employee_profile.city_name, "Updated City")
        self.assertEqual(employee_profile.biography, "Updated biography")

class SocialAuthenticationTests(TestCase):
    def setUp(self):
        # Setup test client and common test data
        self.client = APIClient()
        self.google_login_url = reverse("google_signin")
        self.apple_login_url = reverse("apple_signin")

    def test_google_signin_new_user(self):
        # Mock the Google token verification
        with patch("google.oauth2.id_token.verify_firebase_token") as mock_verify:
            # Setup mock return value for token verification
            mock_verify.return_value = {
                "email": "newuser@gmail.com",
                "name": "Test User",
            }

            # Prepare test data
            payload = {"id_token": "mock_google_token"}

            # Make the request
            response = self.client.post(self.google_login_url, payload, format="json")

            # Assertions
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["message"], "Google Login successful")
            self.assertTrue(response.data["created"])
            self.assertIsNotNone(response.data["access"])
            self.assertIsNotNone(response.data["refresh"])

            # Verify user was created
            user = User.objects.get(email="newuser@gmail.com")
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "newuser@gmail.com")

    def test_google_signin_existing_user(self):
        # Create an existing user
        existing_user = User.objects.create_user(
            username="existinguser@gmail.com",
            email="existinguser@gmail.com",
            password="testpass123",
        )

        # Mock the Google token verification
        with patch("google.oauth2.id_token.verify_firebase_token") as mock_verify:
            # Setup mock return value for token verification
            mock_verify.return_value = {
                "email": "existinguser@gmail.com",
                "name": "Existing User",
            }

            # Prepare test data
            payload = {"id_token": "mock_google_token"}

            # Make the request
            response = self.client.post(self.google_login_url, payload, format="json")

            # Assertions
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["message"], "Google Login successful")
            self.assertEqual(response.data["user"], "existinguser@gmail.com")
            self.assertFalse(response.data["created"])
            self.assertIsNotNone(response.data["access"])
            self.assertIsNotNone(response.data["refresh"])

    # Other social authentication tests remain the same
