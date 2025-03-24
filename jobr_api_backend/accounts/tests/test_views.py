from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.cache import cache
from django.contrib.auth import get_user_model
from unittest.mock import patch, Mock
from django.core.exceptions import ValidationError

from ..models import ProfileOption, Employee, Employer
from ..services import VATValidationService

User = get_user_model()

class UserViewSetTests(APITestCase):
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'username': 'testuser@example.com',
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'role': ProfileOption.EMPLOYEE
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)

    def test_list_users(self):
        """Test listing users."""
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_user(self):
        """Test retrieving a specific user."""
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])

    def test_create_user(self):
        """Test creating a new user."""
        url = reverse('user-list')
        new_user_data = {
            'username': 'newuser@example.com',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'role': ProfileOption.EMPLOYER
        }
        response = self.client.post(url, new_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_update_user(self):
        """Test updating a user."""
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        update_data = {'email': 'updated@example.com'}
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'updated@example.com')

class VATValidationTests(APITestCase):
    def setUp(self):
        self.url = reverse('validate-vat')
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        self.client.force_authenticate(user=self.user)
        cache.clear()  # Clear cache before each test

    def test_valid_belgian_vat_number(self):
        """Test validation with a valid Belgian VAT number"""
        valid_vat = "BE0123456789"
        mock_company_details = {
            "name": "Test Company",
            "street_name": "Test Street",
            "house_number": "123",
            "city": "Brussels",
            "postal_code": "1000",
            "country": "Belgium"
        }

        with patch.object(
            VATValidationService,
            'validate_vat',
            return_value={'is_valid': True, 'company_details': mock_company_details}
        ):
            response = self.client.post(self.url, {'vat_number': valid_vat})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['is_valid'])
            self.assertEqual(response.data['company_details'], mock_company_details)

    def test_invalid_vat_format(self):
        """Test validation with incorrect VAT number format"""
        invalid_vat = "BE123"  # Invalid format
        response = self.client.post(self.url, {'vat_number': invalid_vat})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'INVALID_FORMAT')

    def test_non_belgian_vat(self):
        """Test validation with non-Belgian VAT number"""
        non_be_vat = "FR12345678901"
        response = self.client.post(self.url, {'vat_number': non_be_vat})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'INVALID_FORMAT')

    def test_nonexistent_vat(self):
        """Test validation with non-existent VAT number"""
        with patch.object(
            VATValidationService,
            'validate_vat',
            side_effect=ValidationError({
                'error': 'VAT_NOT_FOUND',
                'message': 'VAT number not found in database'
            })
        ):
            response = self.client.post(self.url, {'vat_number': 'BE0123456789'})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['error'], 'VAT_NOT_FOUND')

    def test_company_details_cache(self):
        """Test caching mechanism"""
        vat_number = "BE0123456789"
        mock_company_details = {
            "name": "Test Company",
            "street_name": "Test Street",
            "house_number": "123",
            "city": "Brussels",
            "postal_code": "1000",
            "country": "Belgium"
        }
        mock_result = {'is_valid': True, 'company_details': mock_company_details}

        with patch.object(
            VATValidationService,
            'validate_vat',
            return_value=mock_result
        ) as mock_validate:
            response1 = self.client.post(self.url, {'vat_number': vat_number})
            self.assertEqual(response1.status_code, status.HTTP_200_OK)
            mock_validate.assert_called_once()

            # Second request - should use cache
            response2 = self.client.post(self.url, {'vat_number': vat_number})
            self.assertEqual(response2.status_code, status.HTTP_200_OK)
            mock_validate.assert_called_once()

    def test_vat_validation_error_handling(self):
        """Test error handling for service failures"""
        with patch.object(
            VATValidationService,
            'validate_vat',
            side_effect=Exception('Service unavailable')
        ):
            response = self.client.post(self.url, {'vat_number': 'BE0123456789'})
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertEqual(response.data['error'], 'SERVICE_UNAVAILABLE')

    def test_authentication_required(self):
        """Test that authentication is required"""
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {'vat_number': 'BE0123456789'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_vat_number(self):
        """Test validation with missing VAT number"""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        cache.clear()  # Clear cache after each test

class EmployeeSearchViewTests(APITestCase):
    def setUp(self):
        """Set up test data."""
        self.employer = User.objects.create_user(
            username='employer@test.com',
            email='employer@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        self.employee = User.objects.create_user(
            username='employee@test.com',
            email='employee@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        Employee.objects.filter(user=self.employee).update(
            city_name='Test City'
        )
        self.client.force_authenticate(user=self.employer)

    def test_search_employees(self):
        """Test searching for employees."""
        url = reverse('employee-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_employees_by_city(self):
        """Test searching for employees by city."""
        url = reverse('employee-search') + '?city=Test'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['city'], 'Test City')

class EmployerSearchViewTests(APITestCase):
    def setUp(self):
        """Set up test data."""
        self.employee = User.objects.create_user(
            username='employee@test.com',
            email='employee@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.employer = User.objects.create_user(
            username='employer@test.com',
            email='employer@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        Employer.objects.filter(user=self.employer).update(
            company_name='Test Company'
        )
        self.client.force_authenticate(user=self.employee)

    def test_search_employers(self):
        """Test searching for employers."""
        url = reverse('employer-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_employers_by_company(self):
        """Test searching for employers by company name."""
        url = reverse('employer-search') + '?company=Test'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company_name'], 'Test Company')