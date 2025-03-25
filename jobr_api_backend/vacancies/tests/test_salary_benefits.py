from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import SalaryBenefit
from accounts.models import CustomUser, ProfileOption

class SalaryBenefitTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        self.client.force_authenticate(user=self.user)

        # Create some test salary benefits
        self.benefit1 = SalaryBenefit.objects.create(
            name='Health Insurance',
            weight=10
        )
        self.benefit2 = SalaryBenefit.objects.create(
            name='Company Car',
            weight=8
        )

    def test_list_salary_benefits(self):
        """Test retrieving a list of salary benefits."""
        url = reverse('vacancies:salary-benefit-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Health Insurance')
        self.assertEqual(response.data[1]['name'], 'Company Car')

    def test_retrieve_salary_benefit(self):
        """Test retrieving a single salary benefit."""
        url = reverse('vacancies:salary-benefit-detail', args=[self.benefit1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Health Insurance')
        self.assertEqual(response.data['weight'], 10)

    def test_create_salary_benefit_not_allowed(self):
        """Test creating a salary benefit is not allowed (read-only)."""
        url = reverse('vacancies:salary-benefit-list')
        data = {
            'name': 'Meal Vouchers',
            'weight': 5
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_salary_benefit_not_allowed(self):
        """Test updating a salary benefit is not allowed (read-only)."""
        url = reverse('vacancies:salary-benefit-detail', args=[self.benefit1.id])
        data = {
            'name': 'Updated Health Insurance',
            'weight': 12
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_salary_benefit_not_allowed(self):
        """Test deleting a salary benefit is not allowed (read-only)."""
        url = reverse('vacancies:salary-benefit-detail', args=[self.benefit1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthenticated_access(self):
        """Test that unauthenticated access is not allowed."""
        self.client.force_authenticate(user=None)
        url = reverse('vacancies:salary-benefit-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)