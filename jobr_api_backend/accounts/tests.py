from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser, Employee

from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from datetime import date

User = get_user_model()


class UserTests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='securepassword'
        )

    def test_employee_registration_cycle(self):
        register_url = reverse('employee-registration')
        register_data = {
            'username': 'newemployee',
            'email': 'employee@example.com',
            'password': 'newpassword',
            'date_of_birth': '1990-01-01',  # Add required employee fields
            'gender': 'male',
            'phone_number': '1234567890'
        }
        register_response = self.client.post(register_url, register_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('access' in register_response.data)
        self.assertTrue('refresh' in register_response.data)

    def test_login_and_access(self):
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'securepassword'
        }
        login_response = self.client.post(login_url, login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response.data)
        self.assertTrue('refresh' in login_response.data)

    def test_token_refresh(self):
        # First login
        login_url = reverse('login')
        login_response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'securepassword'
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        # Extract refresh token
        refresh_token = login_response.data.get('refresh')
        self.assertIsNotNone(refresh_token, "No refresh token in response")

        # Try refresh
        refresh_url = reverse('token_refresh')
        refresh_response = self.client.post(refresh_url, {
            'refresh': refresh_token
        })
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(refresh_response.data.get('access'))

    def test_protected_endpoint_without_token(self):
        # Try to access protected endpoint without token
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_update(self):
        # First get tokens through login
        login_url = reverse('login')
        login_response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'securepassword'
        }, format='json')
        
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        
        update_data = {
            'username': 'updateduser',
            'email': 'updated@example.com'
        }
        
        response = self.client.patch(url, update_data, format='json')  # Using PATCH instead of PUT
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'updated@example.com')

    def test_user_delete(self):
        # Get token first
        login_url = reverse('login')
        login_response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'securepassword'
        })
        token = login_response.data['access']
        
        # Use token for delete
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(id=self.user.id).exists())  # Verify user no longer exists


class SocialAuthenticationTests(TestCase):
    def setUp(self):
        # Setup test client and common test data
        self.client = APIClient()
        self.google_login_url = reverse('google_signin')
        self.apple_login_url = reverse('apple_signin')

    def test_google_signin_new_user(self):
        # Mock the Google token verification
        with patch('google.oauth2.id_token.verify_firebase_token') as mock_verify:
            # Setup mock return value for token verification
            mock_verify.return_value = {
                'email': 'newuser@gmail.com',
                'name': 'Test User',
            }

            # Prepare test data
            payload = {
                'id_token': 'mock_google_token'
            }

            # Make the request
            response = self.client.post(self.google_login_url, payload, format='json')

            # Assertions
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['message'], 'Google Login successful')
            self.assertTrue(response.data['created'])
            self.assertIsNotNone(response.data['access'])
            self.assertIsNotNone(response.data['refresh'])
            
            # Verify user was created
            user = User.objects.get(email='newuser@gmail.com')
            self.assertIsNotNone(user)
            self.assertEqual(user.username, 'newuser@gmail.com')

    def test_google_signin_existing_user(self):
        # Create an existing user
        existing_user = User.objects.create_user(
            username='existinguser@gmail.com',
            email='existinguser@gmail.com',
            password='testpass123'
        )

        # Mock the Google token verification
        with patch('google.oauth2.id_token.verify_firebase_token') as mock_verify:
            # Setup mock return value for token verification
            mock_verify.return_value = {
                'email': 'existinguser@gmail.com',
                'name': 'Existing User',
            }

            # Prepare test data
            payload = {
                'id_token': 'mock_google_token'
            }

            # Make the request
            response = self.client.post(self.google_login_url, payload, format='json')

            # Assertions
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['message'], 'Google Login successful')
            self.assertEqual(response.data['user'], 'existinguser@gmail.com')
            self.assertFalse(response.data['created'])
            self.assertIsNotNone(response.data['access'])
            self.assertIsNotNone(response.data['refresh'])

    def test_apple_signin_new_user(self):
        # Mock the Firebase token verification
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            # Setup mock return value for token verification
            mock_verify.return_value = {
                'email': 'newappleuser@example.com',
                'uid': 'apple_unique_id_123'
            }

            # Prepare test data
            payload = {
                'id_token': 'mock_apple_token'
            }

            # Make the request
            response = self.client.post(self.apple_login_url, payload, format='json')

            # Assertions
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['message'], 'Apple Login successful')
            self.assertTrue(response.data['created'])
            self.assertIsNotNone(response.data['access'])
            self.assertIsNotNone(response.data['refresh'])
            
            # Verify user was created
            user = User.objects.get(email='newappleuser@example.com')
            self.assertIsNotNone(user)
            self.assertEqual(user.username, 'apple_apple_unique_id_123')

    def test_apple_signin_existing_user(self):
        # Create an existing user
        existing_user = User.objects.create_user(
            username='existingappleuser@example.com',
            email='existingappleuser@example.com',
            password='testpass123'
        )

        # Mock the Firebase token verification
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            # Setup mock return value for token verification
            mock_verify.return_value = {
                'email': 'existingappleuser@example.com',
                'uid': 'apple_existing_id'
            }

            # Prepare test data
            payload = {
                'id_token': 'mock_apple_token'
            }

            # Make the request
            response = self.client.post(self.apple_login_url, payload, format='json')

            # Assertions
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['message'], 'Apple Login successful')
            self.assertEqual(response.data['user'], 'existingappleuser@example.com')
            self.assertFalse(response.data['created'])
            self.assertIsNotNone(response.data['access'])
            self.assertIsNotNone(response.data['refresh'])

    def test_google_signin_invalid_token(self):
        # Mock the Google token verification to raise an error
        with patch('google.oauth2.id_token.verify_firebase_token') as mock_verify:
            # Simulate token verification failure
            mock_verify.side_effect = ValueError('Invalid token')

            # Prepare test data
            payload = {
                'id_token': 'invalid_token'
            }

            # Make the request
            response = self.client.post(self.google_login_url, payload, format='json')

            # Assertions
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid token', str(response.data))

    def test_apple_signin_invalid_token(self):
        # Mock the Firebase token verification to raise an error
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            # Simulate token verification failure
            from firebase_admin import auth as firebase_auth
            mock_verify.side_effect = firebase_auth.InvalidIdTokenError('Invalid token')

            # Prepare test data
            payload = {
                'id_token': 'invalid_token'
            }

            # Make the request
            response = self.client.post(self.apple_login_url, payload, format='json')

            # Assertions
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid token', str(response.data))

    def test_missing_token(self):
        # Test Google Sign-in without token
        response_google = self.client.post(self.google_login_url, {}, format='json')
        self.assertEqual(response_google.status_code, 400)
        self.assertEqual(response_google.data['error'], 'ID token is required')

        # Test Apple Sign-in without token
        response_apple = self.client.post(self.apple_login_url, {}, format='json')
        self.assertEqual(response_apple.status_code, 400)
        self.assertEqual(response_apple.data['error'], 'ID token is required')

class EmployeeStatisticsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)


    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.employee = Employee.objects.create(
            user=self.user, 
            date_of_birth=date(1990, 1, 1)  # Added a sample date of birth haha
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_statistics(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('employee-statistics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_increment_phone_sessions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('employee-statistics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)