from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import CustomUser, Employee, Employer, ProfileOption
from vacancies.models import (
    Location,
    ContractType,
    Function,
    Language,
    Question,
    Skill,
    Vacancy,
    ApplyVacancy,
    MasteryOption
)
from decimal import Decimal
from django.utils import timezone
from math import radians

class BaseViewTests(APITestCase):
    def setUp(self):
        """
        Set up test data for base view tests
        """
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            role=ProfileOption.EMPLOYER
        )
        
        # Create test data
        self.location = Location.objects.create(location='Brussels', weight=3)
        self.contract_type = ContractType.objects.create(contract_type='Full-time', weight=2)
        self.function = Function.objects.create(function='Developer', weight=4)
        self.language = Language.objects.create(language='English', weight=5)
        self.question = Question.objects.create(question='Experience?', weight=1)
        self.skill = Skill.objects.create(skill='Python', category='hard', weight=5)
        
        # Set up client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_locations_view(self):
        """
        Test LocationsView
        """
        url = reverse('locations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['location'], 'Brussels')

    def test_skills_view(self):
        """
        Test SkillsView
        """
        url = reverse('skills')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['skill'], 'Python')

    def test_languages_view(self):
        """
        Test LanguagesView
        """
        url = reverse('languages')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['language'], 'English')

    def test_functions_view(self):
        """
        Test FunctionsView
        """
        url = reverse('functions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['function'], 'Developer')

    def test_questions_view(self):
        """
        Test QuestionsView
        """
        url = reverse('questions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['question'], 'Experience?')

    def test_contract_types_view(self):
        """
        Test ContractsTypesView
        """
        url = reverse('contracts')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['contract_type'], 'Full-time')

class VacancyViewSetTests(APITestCase):
    def setUp(self):
        """
        Set up test data for VacancyViewSet tests
        """
        # Create employer
        self.employer = CustomUser.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYER
        )
        self.employer.save()  # Save first to get an ID
        
        # Create base models
        self.location = Location.objects.create(location='Brussels', weight=3)
        self.function = Function.objects.create(function='Developer', weight=4)
        
        # Create vacancy
        self.vacancy = Vacancy.objects.create(
            employer=self.employer,
            expected_mastery=MasteryOption.ADVANCED,
            location=self.location,
            function=self.function,
            job_date=timezone.now().date(),
            salary=Decimal('50000.00')
        )
        
        # Set up client
        self.client = APIClient()
        self.client.force_authenticate(user=self.employer)

    def test_list_vacancies(self):
        """
        Test listing vacancies
        """
        url = reverse('vacancy-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['employer']['username'], 'employer')

    def test_create_vacancy(self):
        """
        Test creating a vacancy
        """
        url = reverse('vacancy-list')
        data = {
            'expected_mastery': MasteryOption.ADVANCED,
            'location': {'id': self.location.id},
            'function': {'id': self.function.id},
            'job_date': timezone.now().date().isoformat(),
            'salary': '60000.00'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vacancy.objects.count(), 2)

    def test_retrieve_vacancy(self):
        """
        Test retrieving a specific vacancy
        """
        url = reverse('vacancy-detail', kwargs={'pk': self.vacancy.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.vacancy.id)

class VacancyFilterViewTests(APITestCase):
    def setUp(self):
        """
        Set up test data for VacancyFilterView tests
        """
        # Create employer and employee
        self.employer = CustomUser.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYER
        )
        self.employer.save()  # Save first to get an ID
        
        self.employee = CustomUser.objects.create_user(
            username='employee',
            email='employee@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE
        )
        
        # Create employee profile
        self.employee_profile = Employee.objects.create(
            date_of_birth='1990-01-01',
            gender='male',
            phone_number='1234567890',
            latitude=50.8503,  # Brussels latitude
            longitude=4.3517   # Brussels longitude
        )
        
        # Create base models
        self.contract_type = ContractType.objects.create(contract_type='Full-time')
        self.function = Function.objects.create(function='Developer')
        self.skill = Skill.objects.create(skill='Python', category='hard')
        
        # Create vacancies
        self.vacancy1 = Vacancy.objects.create(
            employer=self.employer,
            salary=Decimal('50000.00'),
            latitude=50.8503,  # Brussels
            longitude=4.3517
        )
        self.vacancy2 = Vacancy.objects.create(
            employer=self.employer,
            salary=Decimal('60000.00'),
            latitude=51.5074,  # London
            longitude=-0.1278
        )
        
        # Add relationships
        self.vacancy1.contract_type.add(self.contract_type)
        self.vacancy1.skill.add(self.skill)
        
        # Set up client
        self.client = APIClient()
        self.client.force_authenticate(user=self.employee)

    def test_filter_by_contract_type(self):
        """
        Test filtering vacancies by contract type
        """
        url = reverse('vacancy-filter')
        response = self.client.get(f"{url}?contract_type={self.contract_type.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.vacancy1.id)

    def test_filter_by_skills(self):
        """
        Test filtering vacancies by skills
        """
        url = reverse('vacancy-filter')
        response = self.client.get(f"{url}?skills={self.skill.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.vacancy1.id)

    def test_sort_by_salary(self):
        """
        Test sorting vacancies by salary
        """
        url = reverse('vacancy-filter')
        
        # Test ascending order
        response = self.client.get(f"{url}?sort_by_salary=asc")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.vacancy1.id)
        self.assertEqual(response.data[1]['id'], self.vacancy2.id)
        
        # Test descending order
        response = self.client.get(f"{url}?sort_by_salary=desc")
        self.assertEqual(response.data[0]['id'], self.vacancy2.id)
        self.assertEqual(response.data[1]['id'], self.vacancy1.id)