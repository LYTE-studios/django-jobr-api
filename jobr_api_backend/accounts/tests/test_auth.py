from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import CustomUser, ProfileOption

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.test_connection_url = reverse('test-connection')
        
        # Create a test user
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'username': 'test@example.com',
            'role': ProfileOption.EMPLOYEE
        }
        self.user = CustomUser.objects.create_user(**self.user_data)

    def test_user_registration(self):
        """Test user registration endpoint."""
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'username': 'newuser@example.com',
            'role': ProfileOption.EMPLOYER
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], data['email'])
        self.assertEqual(response.data['user']['role'], data['role'])

    def test_user_login(self):
        """Test user login endpoint."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], data['email'])

    def test_invalid_login(self):
        """Test login with invalid credentials."""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_test_connection_authenticated(self):
        """Test connection endpoint with valid token."""
        # First login to get the token
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        login_response = self.client.post(self.login_url, login_data)
        token = login_response.data['access']

        # Test the connection with the token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.test_connection_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Connection successful')
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], login_data['email'])

    def test_test_connection_unauthenticated(self):
        """Test connection endpoint without token."""
        response = self.client.get(self.test_connection_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_registration_validation(self):
        """Test registration with invalid data."""
        # Test missing required fields
        data = {'email': 'newuser@example.com'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid email format
        data = {
            'email': 'invalid-email',
            'password': 'newpass123',
            'username': 'invalid-email',
            'role': ProfileOption.EMPLOYER
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test duplicate email
        data = {
            'email': 'test@example.com',  # Already exists
            'password': 'newpass123',
            'username': 'test@example.com',
            'role': ProfileOption.EMPLOYER
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)