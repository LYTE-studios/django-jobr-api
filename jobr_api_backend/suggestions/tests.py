from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from accounts.models import CustomUser, Employee, Company, CompanyUser
from vacancies.models import Vacancy
from .models import AISuggestion, SuggestionWeight


class SuggestionWeightTests(TestCase):
    def setUp(self):
        self.weight = SuggestionWeight.objects.create(
            name='distance',
            weight=50,
            field_type='quantitative'
        )

    def test_weight_str(self):
        self.assertEqual(str(self.weight), 'distance: 50%')

    def test_weight_with_mastery(self):
        weight = SuggestionWeight.objects.create(
            name='skills',
            weight=30,
            mastery_level='intermediate',
            field_type='quantitative'
        )
        self.assertEqual(str(weight), 'skills (intermediate): 30%')


class AISuggestionTests(TransactionTestCase):
    def setUp(self):
        # Create test users
        self.employee_user = CustomUser.objects.create_user(
            username='employee1@test.com',
            email='employee1@test.com',
            password='testpass123',
            role='employee'
        )
        self.employer_user = CustomUser.objects.create_user(
            username='employer1@test.com',
            email='employer1@test.com',
            password='testpass123',
            role='employer'
        )

        # Get the automatically created employee
        self.employee = Employee.objects.get(user=self.employee_user)
        self.employee.biography = 'Test bio'
        self.employee.save()

        # Create company and link it to employer
        self.company = Company.objects.create(
            name='Test Company',
            description='Test company description',
            latitude=50.8503,
            longitude=4.3517
        )
        CompanyUser.objects.create(
            company=self.company,
            user=self.employer_user,
            role='owner'
        )

        # Create vacancy
        self.vacancy = Vacancy.objects.create(
            company=self.company,
            title='Test Vacancy',
            description='Test description'
        )

        # Create suggestion
        self.suggestion = AISuggestion.objects.create(
            employee=self.employee,
            vacancy=self.vacancy,
            quantitative_score=75.0,
            qualitative_score=85.0,
            total_score=80.0,
            message='Test suggestion message'
        )

    def test_suggestion_str(self):
        expected = f'Match: {self.employee} - {self.vacancy} (Score: 80.0)'
        self.assertEqual(str(self.suggestion), expected)


class AISuggestionAPITests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.employee_user = CustomUser.objects.create_user(
            username='employee2@test.com',
            email='employee2@test.com',
            password='testpass123',
            role='employee'
        )
        self.employer_user = CustomUser.objects.create_user(
            username='employer2@test.com',
            email='employer2@test.com',
            password='testpass123',
            role='employer'
        )

        # Get the automatically created employee
        self.employee = Employee.objects.get(user=self.employee_user)
        self.employee.biography = 'Test bio'
        self.employee.save()

        # Create company and link it to employer
        self.company = Company.objects.create(
            name='Test Company',
            description='Test company description',
            latitude=50.8503,
            longitude=4.3517
        )
        CompanyUser.objects.create(
            company=self.company,
            user=self.employer_user,
            role='owner'
        )

        # Create vacancy
        self.vacancy = Vacancy.objects.create(
            company=self.company,
            title='Test Vacancy',
            description='Test description'
        )

        # Create suggestion
        self.suggestion = AISuggestion.objects.create(
            employee=self.employee,
            vacancy=self.vacancy,
            quantitative_score=75.0,
            qualitative_score=85.0,
            total_score=80.0,
            message='Test suggestion message'
        )

        # Authenticate
        self.client.force_authenticate(user=self.employee_user)

    def test_list_suggestions(self):
        url = reverse('suggestion-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_suggestion(self):
        url = reverse('suggestion-detail', args=[self.suggestion.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_score'], 80.0)

    def test_create_suggestion_not_allowed(self):
        url = reverse('suggestion-list')
        data = {
            'employee': self.employee.id,
            'vacancy': self.vacancy.id,
            'quantitative_score': 75.0,
            'qualitative_score': 85.0,
            'total_score': 80.0,
            'message': 'Test message'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_suggestion_not_allowed(self):
        url = reverse('suggestion-detail', args=[self.suggestion.id])
        data = {'message': 'Updated message'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_suggestion_not_allowed(self):
        url = reverse('suggestion-detail', args=[self.suggestion.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
