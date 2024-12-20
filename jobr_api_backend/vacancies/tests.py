from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date
from decimal import Decimal
from accounts.models import Employer, Employee, CustomUser
from common.models import ContractType, Function, Question, Skill, Language
from vacancies.models import Vacancy, ApplyVacancy
from vacancies.serializers import VacancySerializer, ApplySerializer

class VacancyTests(APITestCase):
    def setUp(self):
        # Create basic models first
        self.contract_type = ContractType.objects.create(contract_type="Full-time")
        self.function = Function.objects.create(function="Software Development")
        self.skill = Skill.objects.create(skill="Python", category="Programming")
        self.language = Language.objects.create(language="English")
        self.question = Question.objects.create(question="What is your experience?")

        # Then create user and related models
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.employer = Employer.objects.create(
            user=self.user,
            company_name="Test Company",
            coordinates="40.7128,-74.0060"
        )

        # Create employee user
        self.employee_user = CustomUser.objects.create_user(
            username='employeeuser',
            email='employee@example.com',
            password='testpass123'
        )
        
        self.employee = Employee.objects.create(
            user=self.employee_user,
            latitude=40.7128,
            longitude=-74.0060,
            date_of_birth=date(1990, 1, 1),
        )
        
        # Create vacancy last
        self.vacancy = Vacancy.objects.create(
            employer=self.employer,
            title="Test Position",
            contract_type=self.contract_type,
            function=self.function,
            location="distance",
            week_day="Monday-Friday",
            salary=Decimal('50000.00'),
            description="Test description",
            latitude=40.7128,
            longitude=-74.0060
        )
        
        # Add many-to-many relationships after creation
        self.vacancy.skill.set([self.skill])
        self.vacancy.language.set([self.language])
        self.vacancy.question.set([self.question])

        # Set up authentication
        self.client = APIClient()
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data.get('access')
        if self.token is None:
            self.fail("Access token not found in response data")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
class VacancyModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.employer = Employer.objects.create(
            user=self.user,
            company_name="Test Company",
            coordinates="40.7128,-74.0060"  # Added coordinates
        )
        self.contract_type = ContractType.objects.create(contract_type="Full-time")
        self.function = Function.objects.create(function="Software Development")

    def test_vacancy_creation(self):
        """Test the creation of a Vacancy instance"""
        vacancy = Vacancy.objects.create(
            employer=self.employer,
            title="Test Position",
            contract_type=self.contract_type,
            function=self.function,
            location="distance",
            week_day="Monday-Friday",
            salary=Decimal('50000.00'),
            description="Test description",
            latitude=40.7128,
            longitude=-74.0060
        )
        self.assertEqual(vacancy.title, "Test Position")
        self.assertEqual(vacancy.salary, Decimal('50000.00'))

class SerializerTests(TestCase):
    def setUp(self):
        self.language = Language.objects.create(language="English")
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.employer = Employer.objects.create(
            user=self.user,
            company_name="Test Company",
            coordinates="40.7128,-74.0060"  # Added coordinates
        )
        self.contract_type = ContractType.objects.create(contract_type="Full-time")
        self.function = Function.objects.create(function="Software Development")

    def test_vacancy_serializer(self):
        """Test VacancySerializer"""
        vacancy = Vacancy.objects.create(
            employer=self.employer,
            title="Test Position",
            contract_type=self.contract_type,
            function=self.function,
            location="distance",
            week_day="Monday-Friday",
            salary=Decimal('50000.00'),
            description="Test description",
            latitude=40.7128,
            longitude=-74.0060
        )
        serializer = VacancySerializer(vacancy)
        self.assertEqual(serializer.data['title'], "Test Position")
        self.assertEqual(serializer.data['employer'], self.employer.id)