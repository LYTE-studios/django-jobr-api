from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import CustomUser, Employee, Employer, ProfileOption

class ProfileUpdateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.client.force_authenticate(user=self.user)
        self.profile_url = reverse('profile-profile')

    def test_get_own_profile(self):
        """Test retrieving own profile."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_update_employee_profile(self):
        """Test updating employee profile data."""
        data = {
            'employee_profile': {
                'phone_number': '1234567890',
                'city_name': 'Brussels',
                'biography': 'Test bio'
            }
        }
        response = self.client.put(self.profile_url, data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print("Response content:", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.employee_profile.phone_number, '1234567890')
        self.assertEqual(self.user.employee_profile.city_name, 'Brussels')
        self.assertEqual(self.user.employee_profile.biography, 'Test bio')

    def test_update_employer_profile(self):
        """Test updating employer profile data."""
        # Change user to employer
        self.user.role = ProfileOption.EMPLOYER
        self.user.save()
        
        data = {
            'employer_profile': {
                'company_name': 'Test Company',
                'vat_number': 'BE0123456789',
                'city': 'Antwerp',
                'website': 'https://example.com'
            }
        }
        response = self.client.put(self.profile_url, data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print("Response content:", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.employer_profile.company_name, 'Test Company')
        self.assertEqual(self.user.employer_profile.vat_number, 'BE0123456789')
        self.assertEqual(self.user.employer_profile.city, 'Antwerp')
        self.assertEqual(self.user.employer_profile.website, 'https://example.com')

    def test_partial_profile_update(self):
        """Test partial update of profile data."""
        data = {
            'employee_profile': {
                'phone_number': '1234567890'
            }
        }
        response = self.client.patch(self.profile_url, data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print("Response content:", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.employee_profile.phone_number, '1234567890')

    def test_update_wrong_profile_type(self):
        """Test updating wrong profile type based on role."""
        data = {
            'employer_profile': {
                'company_name': 'Test Company'
            }
        }
        response = self.client.put(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(hasattr(self.user, 'employer_profile'))

    def test_update_user_names(self):
        """Test updating user's first and last name."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = self.client.put(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')