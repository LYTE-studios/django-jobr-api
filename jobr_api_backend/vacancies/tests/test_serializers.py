from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from accounts.models import CustomUser, Employee, Employer, ProfileOption
from vacancies.models import (
    Location,
    ContractType,
    Function,
    Language,
    Question,
    Skill,
    Vacancy,
    VacancyLanguage,
    VacancyDescription,
    VacancyQuestion,
    ApplyVacancy,
    MasteryOption
)
from vacancies.serializers import (
    LocationSerializer,
    ContractTypeSerializer,
    FunctionSerializer,
    LanguageSerializer,
    QuestionSerializer,
    SkillSerializer,
    VacancyLanguageSerializer,
    VacancyDescriptionSerializer,
    VacancyQuestionSerializer,
    VacancySerializer,
    ApplySerializer
)
from decimal import Decimal
from django.utils import timezone

User = get_user_model()

class BaseSerializerTests(TestCase):
    def setUp(self):
        """
        Set up test data for base serializer tests
        """
        self.location = Location.objects.create(location='Brussels', weight=3)
        self.contract_type = ContractType.objects.create(contract_type='Full-time', weight=2)
        self.function = Function.objects.create(function='Developer', weight=4)
        self.language = Language.objects.create(language='English', weight=5)
        self.question = Question.objects.create(question='Experience?', weight=1)
        self.skill = Skill.objects.create(skill='Python', category='hard', weight=5)

    def test_location_serializer(self):
        """
        Test LocationSerializer
        """
        serializer = LocationSerializer(self.location)
        self.assertEqual(serializer.data['location'], 'Brussels')
        self.assertIn('id', serializer.data)

    def test_contract_type_serializer(self):
        """
        Test ContractTypeSerializer
        """
        serializer = ContractTypeSerializer(self.contract_type)
        self.assertEqual(serializer.data['contract_type'], 'Full-time')
        self.assertIn('id', serializer.data)

    def test_function_serializer(self):
        """
        Test FunctionSerializer
        """
        serializer = FunctionSerializer(self.function)
        self.assertEqual(serializer.data['function'], 'Developer')
        self.assertIn('id', serializer.data)

    def test_language_serializer(self):
        """
        Test LanguageSerializer
        """
        serializer = LanguageSerializer(self.language)
        self.assertEqual(serializer.data['language'], 'English')
        self.assertIn('id', serializer.data)

    def test_question_serializer(self):
        """
        Test QuestionSerializer
        """
        serializer = QuestionSerializer(self.question)
        self.assertEqual(serializer.data['question'], 'Experience?')

    def test_skill_serializer(self):
        """
        Test SkillSerializer
        """
        serializer = SkillSerializer(self.skill)
        self.assertEqual(serializer.data['skill'], 'Python')
        self.assertEqual(serializer.data['category'], 'hard')
        self.assertIn('id', serializer.data)

class VacancySerializerTests(TestCase):
    def setUp(self):
        """
        Set up test data for VacancySerializer tests
        """
        # Create employer
        self.employer = CustomUser.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYER
        )
        self.employer.save()  # Save to ensure employer_profile is created
        
        # Create base models
        self.location = Location.objects.create(location='Brussels', weight=3)
        self.function = Function.objects.create(function='Developer', weight=4)
        self.contract_type = ContractType.objects.create(contract_type='Full-time', weight=2)
        self.skill = Skill.objects.create(skill='Python', category='hard', weight=5)
        
        # Create vacancy
        self.vacancy = Vacancy.objects.create(
            employer=self.employer,
            expected_mastery=MasteryOption.ADVANCED,
            location=self.location,
            function=self.function,
            job_date=timezone.now().date(),
            salary=Decimal('50000.00')
        )
        
        # Add many-to-many relationships
        self.vacancy.contract_type.add(self.contract_type)
        self.vacancy.skill.add(self.skill)
        
        # Create request factory
        self.factory = APIRequestFactory()

    def test_vacancy_serialization(self):
        """
        Test serializing a Vacancy instance
        """
        serializer = VacancySerializer(self.vacancy)
        data = serializer.data
        
        self.assertEqual(data['employer']['username'], 'employer')
        self.assertEqual(data['expected_mastery'], MasteryOption.ADVANCED)
        self.assertEqual(data['location']['location'], 'Brussels')
        self.assertEqual(data['function']['function'], 'Developer')
        self.assertEqual(data['salary'], '50000.00')
        
        # Test related fields
        self.assertEqual(len(data['contract_type']), 1)
        self.assertEqual(data['contract_type'][0]['contract_type'], 'Full-time')
        self.assertEqual(len(data['skill']), 1)
        self.assertEqual(data['skill'][0]['skill'], 'Python')

    def test_vacancy_creation(self):
        """
        Test creating a Vacancy through serializer
        """
        request = self.factory.post('/vacancies/')
        request.user = self.employer
        
        data = {
            'expected_mastery': MasteryOption.ADVANCED,
            'location': {'id': self.location.id},
            'function': {'id': self.function.id},
            'contract_type': [{'id': self.contract_type.id}],
            'skill': [{'id': self.skill.id}],
            'job_date': timezone.now().date().isoformat(),
            'salary': '60000.00'
        }
        
        serializer = VacancySerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        vacancy = serializer.save()
        self.assertEqual(vacancy.employer, self.employer)
        self.assertEqual(vacancy.location, self.location)
        self.assertEqual(vacancy.function, self.function)
        self.assertEqual(vacancy.salary, Decimal('60000.00'))

class ApplySerializerTests(TestCase):
    def setUp(self):
        """
        Set up test data for ApplySerializer tests
        """
        # Create employer and employee
        self.employer = CustomUser.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYER
        )
        self.employer.save()  # Save to ensure employer_profile is created
        
        self.employee = CustomUser.objects.create_user(
            username='employee',
            email='employee@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE
        )
        self.employee.save()  # Save to ensure employee_profile is created
        
        # Create vacancy
        self.vacancy = Vacancy.objects.create(
            employer=self.employer,
            expected_mastery=MasteryOption.ADVANCED
        )

    def test_apply_serialization(self):
        """
        Test serializing an ApplyVacancy instance
        """
        application = ApplyVacancy.objects.create(
            employee=self.employee,
            vacancy=self.vacancy
        )
        
        serializer = ApplySerializer(application)
        self.assertEqual(serializer.data['employee'], self.employee.id)
        self.assertEqual(serializer.data['vacancy'], self.vacancy.id)

    def test_apply_creation(self):
        """
        Test creating an ApplyVacancy through serializer
        """
        data = {
            'employee': self.employee.id,
            'vacancy': self.vacancy.id
        }
        
        serializer = ApplySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        application = serializer.save()
        self.assertEqual(application.employee, self.employee)
        self.assertEqual(application.vacancy, self.vacancy)