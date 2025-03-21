from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import CustomUser, ProfileOption, Employee
from vacancies.models import (
    Location, Language, Function, Skill, ContractType,
    Vacancy, Sector
)
from decimal import Decimal

class LocationViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.client.force_authenticate(user=self.user)
        self.location1 = Location.objects.create(location='Brussels', weight=1)
        self.location2 = Location.objects.create(location='Antwerp', weight=2)

    def test_get_locations(self):
        """Test retrieving all locations"""
        url = reverse('locations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['location'], 'Brussels')

    def test_get_locations_unauthenticated(self):
        """Test retrieving locations without authentication"""
        self.client.force_authenticate(user=None)
        url = reverse('locations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class LanguageViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.language1 = Language.objects.create(language='English', weight=1)
        self.language2 = Language.objects.create(language='French', weight=2)

    def test_get_languages(self):
        """Test retrieving all languages"""
        url = reverse('languages')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        languages = {item['language'] for item in response.data}
        self.assertEqual(languages, {'English', 'French'})

    def test_get_languages_unauthenticated(self):
        """Test retrieving languages without authentication"""
        self.client.force_authenticate(user=None)
        url = reverse('languages')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class VacancyFilterViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Create test data
        self.employer = CustomUser.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        self.contract_type = ContractType.objects.create(contract_type='Full-time')
        self.function = Function.objects.create(function='Developer')
        self.skill = Skill.objects.create(skill='Python', category='hard')

        # Create vacancies with different salaries and locations
        self.vacancy1 = Vacancy.objects.create(
            employer=self.employer,
            salary=Decimal('50000.00'),
            latitude=50.8503,  # Brussels
            longitude=4.3517
        )
        self.vacancy2 = Vacancy.objects.create(
            employer=self.employer,
            salary=Decimal('60000.00'),
            latitude=51.2194,  # Antwerp (about 51km from Brussels)
            longitude=4.4025
        )

        # Set up user with employee profile and location
        self.user.role = ProfileOption.EMPLOYEE
        self.user.save()
        self.user.employee_profile.latitude = 50.8503  # Brussels
        self.user.employee_profile.longitude = 4.3517
        self.user.employee_profile.save()

        self.vacancy1.contract_type.add(self.contract_type)
        self.vacancy1.skill.add(self.skill)
        self.vacancy2.contract_type.add(self.contract_type)

    def test_filter_by_contract_type(self):
        """Test filtering vacancies by contract type"""
        url = reverse('vacancy-filter')
        response = self.client.get(f"{url}?contract_type={self.contract_type.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_skills(self):
        """Test filtering vacancies by skills"""
        url = reverse('vacancy-filter')
        response = self.client.get(f"{url}?skills={self.skill.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_sort_by_salary_ascending(self):
        """Test sorting vacancies by salary ascending"""
        url = reverse('vacancy-filter')
        response = self.client.get(f"{url}?sort_by_salary=asc")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        salaries = [Decimal(v['salary']) for v in response.data]
        self.assertEqual(salaries, [Decimal('50000.00'), Decimal('60000.00')])

    def test_sort_by_salary_descending(self):
        """Test sorting vacancies by salary descending"""
        url = reverse('vacancy-filter')
        response = self.client.get(f"{url}?sort_by_salary=desc")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        salaries = [Decimal(v['salary']) for v in response.data]
        self.assertEqual(salaries, [Decimal('60000.00'), Decimal('50000.00')])

    def test_filter_by_distance(self):
        """Test filtering vacancies by distance"""
        # Create an employee with location in Brussels
        self.user.role = ProfileOption.EMPLOYEE
        self.user.save()  # This creates the employee profile
        self.user.employee_profile.latitude = 50.8503  # Brussels
        self.user.employee_profile.longitude = 4.3517
        self.user.employee_profile.save()

        url = reverse('vacancy-filter')
        response = self.client.get(f"{url}?employee_id={self.user.employee_profile.id}&distance=50")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only return vacancy1 (Brussels)

class FunctionsViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.sector = Sector.objects.create(name='Technology')
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            sector=self.sector
        )
        self.client.force_authenticate(user=self.user)

        # Create functions in different sectors
        self.function1 = Function.objects.create(
            function='Developer',
            sector=self.sector
        )
        self.function2 = Function.objects.create(
            function='Manager',
            sector=Sector.objects.create(name='Management')
        )

    def test_get_functions_with_sector(self):
        """Test getting functions filtered by user's sector"""
        url = reverse('functions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['function'], 'Developer')

    def test_get_functions_without_sector(self):
        """Test getting all functions when user has no sector"""
        self.user.sector = None
        self.user.save()
        url = reverse('functions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

class ApplyForJobViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employer = CustomUser.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        # Create employee user with profile
        self.employee = CustomUser.objects.create_user(
            username='employee',
            email='employee@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        # Save to trigger profile creation and set location
        self.employee.save()
        self.employee.employee_profile.latitude = 50.8503  # Brussels
        self.employee.employee_profile.longitude = 4.3517
        self.employee.employee_profile.save()
        self.vacancy = Vacancy.objects.create(employer=self.employer)
        self.client.force_authenticate(user=self.employee)

    def test_apply_for_job(self):
        """Test successfully applying for a job"""
        url = reverse('apply', kwargs={'vacancy_id': self.vacancy.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('chatroom', response.data)

    def test_apply_for_nonexistent_job(self):
        """Test applying for a nonexistent job"""
        url = reverse('apply', kwargs={'vacancy_id': 99999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_apply_as_employer(self):
        """Test that employers cannot apply for jobs"""
        self.client.force_authenticate(user=self.employer)
        url = reverse('apply', kwargs={'vacancy_id': self.vacancy.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Only employees can apply for jobs.')