from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser, ProfileOption
from ..models import Vacancy, Function, Skill

class VacancyViewTests(APITestCase):
    def setUp(self):
        """Set up test data."""
        self.employer = CustomUser.objects.create_user(
            username="employer@test.com",
            email="employer@test.com",
            password="testpass123",
            role=ProfileOption.EMPLOYER
        )

        self.employee = CustomUser.objects.create_user(
            username="employee@test.com",
            email="employee@test.com",
            password="testpass123",
            role=ProfileOption.EMPLOYEE
        )

        self.other_employer = CustomUser.objects.create_user(
            username="other@test.com",
            email="other@test.com",
            password="testpass123",
            role=ProfileOption.EMPLOYER
        )

        # Create a vacancy
        self.vacancy = Vacancy.objects.create(
            title="Test Vacancy",
            description="Test Description",
            employer=self.employer.employer_profile,
            salary=50000
        )

    def test_list_vacancies(self):
        """Test listing vacancies."""
        self.client.force_authenticate(user=self.employee)
        url = reverse('vacancies:vacancy-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_vacancy(self):
        """Test creating a new vacancy."""
        self.client.force_authenticate(user=self.employer)
        url = reverse('vacancies:vacancy-list')
        data = {
            'title': 'New Vacancy',
            'description': 'New Description',
            'employer': self.employer.employer_profile.id,
            'salary': 60000
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vacancy.objects.count(), 2)

    def test_update_vacancy(self):
        """Test updating a vacancy."""
        self.client.force_authenticate(user=self.employer)
        url = reverse('vacancies:vacancy-detail', args=[self.vacancy.id])
        data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'employer': self.employer.employer_profile.id,
            'salary': 55000
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vacancy.refresh_from_db()
        self.assertEqual(self.vacancy.title, 'Updated Title')

    def test_delete_vacancy(self):
        """Test deleting a vacancy."""
        self.client.force_authenticate(user=self.employer)
        url = reverse('vacancies:vacancy-detail', args=[self.vacancy.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Vacancy.objects.count(), 0)

    def test_unauthorized_access(self):
        """Test unauthorized access to vacancy operations."""
        url = reverse('vacancies:vacancy-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_vacancies(self):
        """Test filtering vacancies."""
        self.client.force_authenticate(user=self.employee)
        url = reverse('vacancies:vacancy-filter')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_salary(self):
        """Test filtering vacancies by salary range."""
        self.client.force_authenticate(user=self.employee)
        url = f"{reverse('vacancies:vacancy-filter')}?min_salary=40000&max_salary=60000"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_location(self):
        """Test filtering vacancies by location."""
        self.vacancy.latitude = 50.8503
        self.vacancy.longitude = 4.3517
        self.vacancy.save()

        self.client.force_authenticate(user=self.employee)
        url = f"{reverse('vacancies:vacancy-filter')}?max_distance=50"  # 50km radius
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_employer_cannot_modify(self):
        """Test that other employers cannot modify vacancies."""
        self.client.force_authenticate(user=self.other_employer)
        url = reverse('vacancies:vacancy-detail', args=[self.vacancy.id])
        data = {'title': 'Unauthorized Update'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)