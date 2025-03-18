from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import CustomUser, ProfileOption
from vacancies.models import Vacancy, ApplyVacancy
from vacancies.serializers import VacancySerializer

class VacancyViewTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create employer
        self.employer = CustomUser.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYER
        )

        # Create employees
        self.employee1 = CustomUser.objects.create_user(
            username='employee1',
            email='employee1@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE
        )
        self.employee2 = CustomUser.objects.create_user(
            username='employee2',
            email='employee2@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE
        )

        # Create vacancy
        self.vacancy = Vacancy.objects.create(
            employer=self.employer,
            expected_mastery="Advanced"
        )

        # Create applications
        ApplyVacancy.objects.create(
            employee=self.employee1,
            vacancy=self.vacancy
        )
        ApplyVacancy.objects.create(
            employee=self.employee2,
            vacancy=self.vacancy
        )

        # Set up test client
        self.client = APIClient()

    def test_applicant_count(self):
        """Test that vacancy serializer includes applicant count"""
        self.client.force_authenticate(user=self.employer)
        url = reverse('vacancy-detail', kwargs={'pk': self.vacancy.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['applicant_count'], 2)

    def test_get_applicants_as_employer(self):
        """Test getting applicants as the vacancy employer"""
        self.client.force_authenticate(user=self.employer)
        url = reverse('vacancy-applicants', kwargs={'vacancy_id': self.vacancy.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        usernames = {user['username'] for user in response.data['results']}
        self.assertEqual(usernames, {'employee1', 'employee2'})

    def test_get_applicants_as_other_employer(self):
        """Test getting applicants as another employer (should fail)"""
        other_employer = CustomUser.objects.create_user(
            username='other_employer',
            email='other@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYER
        )
        self.client.force_authenticate(user=other_employer)
        url = reverse('vacancy-applicants', kwargs={'vacancy_id': self.vacancy.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_applicants_as_employee(self):
        """Test getting applicants as an employee (should fail)"""
        self.client.force_authenticate(user=self.employee1)
        url = reverse('vacancy-applicants', kwargs={'vacancy_id': self.vacancy.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_applicants_nonexistent_vacancy(self):
        """Test getting applicants for a nonexistent vacancy"""
        self.client.force_authenticate(user=self.employer)
        url = reverse('vacancy-applicants', kwargs={'vacancy_id': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)