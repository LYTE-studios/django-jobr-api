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
    MasteryOption,
    FunctionSkill
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
    ApplySerializer,
    FunctionSkillSerializer
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
        self.skill = Skill.objects.create(skill='Python', category='hard')
        
        # Create function-skill relationship
        self.function_skill = FunctionSkill.objects.create(
            function=self.function,
            skill=self.skill,
            weight=5
        )

    def test_location_serializer(self):
        """Test LocationSerializer"""
        serializer = LocationSerializer(self.location)
        self.assertEqual(serializer.data['location'], 'Brussels')
        self.assertIn('id', serializer.data)

    def test_contract_type_serializer(self):
        """Test ContractTypeSerializer"""
        serializer = ContractTypeSerializer(self.contract_type)
        self.assertEqual(serializer.data['contract_type'], 'Full-time')
        self.assertIn('id', serializer.data)

    def test_function_serializer(self):
        """Test FunctionSerializer with function-skill relationships"""
        serializer = FunctionSerializer(self.function)
        data = serializer.data
        
        # Test basic function data
        self.assertEqual(data['function'], 'Developer')
        self.assertIn('id', data)
        
        # Test function_skills data
        self.assertIn('function_skills', data)
        self.assertEqual(len(data['function_skills']), 1)
        function_skill = data['function_skills'][0]
        self.assertEqual(function_skill['skill']['skill'], 'Python')
        self.assertEqual(function_skill['weight'], 5)

    def test_language_serializer(self):
        """Test LanguageSerializer"""
        serializer = LanguageSerializer(self.language)
        self.assertEqual(serializer.data['language'], 'English')
        self.assertIn('id', serializer.data)

    def test_question_serializer(self):
        """Test QuestionSerializer"""
        serializer = QuestionSerializer(self.question)
        self.assertEqual(serializer.data['question'], 'Experience?')

    def test_skill_serializer(self):
        """Test SkillSerializer"""
        serializer = SkillSerializer(self.skill)
        self.assertEqual(serializer.data['skill'], 'Python')
        self.assertEqual(serializer.data['category'], 'hard')
        self.assertIn('id', serializer.data)

    def test_function_skill_serializer(self):
        """Test FunctionSkillSerializer"""
        serializer = FunctionSkillSerializer(self.function_skill)
        data = serializer.data
        
        self.assertEqual(data['skill']['skill'], 'Python')
        self.assertEqual(data['skill']['category'], 'hard')
        self.assertEqual(data['weight'], 5)

class VacancySerializerTests(TestCase):
    def setUp(self):
        """Set up test data for VacancySerializer tests"""
        # Create employer
        self.employer = CustomUser.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYER
        )
        self.employer.save()
        
        # Create base models
        self.location = Location.objects.create(location='Brussels', weight=3)
        self.function = Function.objects.create(function='Developer', weight=4)
        self.contract_type = ContractType.objects.create(contract_type='Full-time', weight=2)
        self.skill = Skill.objects.create(skill='Python', category='hard')
        
        # Create function-skill relationship
        self.function_skill = FunctionSkill.objects.create(
            function=self.function,
            skill=self.skill,
            weight=5
        )
        
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
        """Test serializing a Vacancy instance"""
        serializer = VacancySerializer(self.vacancy)
        data = serializer.data
        
        self.assertEqual(data['employer']['username'], 'employer')
        self.assertEqual(data['expected_mastery'], MasteryOption.ADVANCED)
        self.assertEqual(data['location']['location'], 'Brussels')
        
        # Test function data including skills
        self.assertEqual(data['function']['function'], 'Developer')
        self.assertEqual(len(data['function']['function_skills']), 1)
        function_skill = data['function']['function_skills'][0]
        self.assertEqual(function_skill['skill']['skill'], 'Python')
        self.assertEqual(function_skill['weight'], 5)
        
        self.assertEqual(data['salary'], '50000.00')
        
        # Test related fields
        self.assertEqual(len(data['contract_type']), 1)
        self.assertEqual(data['contract_type'][0]['contract_type'], 'Full-time')
        self.assertEqual(len(data['skill']), 1)
        self.assertEqual(data['skill'][0]['skill'], 'Python')

    def test_vacancy_creation(self):
        """Test creating a Vacancy through serializer"""
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
        
        # Test basic fields
        self.assertEqual(vacancy.employer, self.employer)
        self.assertEqual(vacancy.expected_mastery, MasteryOption.ADVANCED)
        self.assertEqual(vacancy.location, self.location)
        self.assertEqual(vacancy.function, self.function)
        self.assertEqual(vacancy.salary, Decimal('60000.00'))
        self.assertEqual(vacancy.job_date.isoformat(), data['job_date'])
        
        # Test many-to-many relationships
        self.assertEqual(vacancy.contract_type.count(), 1)
        self.assertEqual(vacancy.skill.count(), 1)
        self.assertIn(self.contract_type, vacancy.contract_type.all())
        self.assertIn(self.skill, vacancy.skill.all())

    def test_vacancy_creation_missing_required_fields(self):
        """Test vacancy creation fails with missing required fields"""
        request = self.factory.post('/vacancies/')
        request.user = self.employer
        
        # Missing required fields
        data = {
            'salary': '60000.00'
        }
        
        serializer = VacancySerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('expected_mastery', serializer.errors)
        self.assertIn('location', serializer.errors)
        self.assertIn('function', serializer.errors)

class ApplySerializerTests(TestCase):
    def setUp(self):
        """Set up test data for ApplySerializer tests"""
        # Create employer and employee
        self.employer = CustomUser.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYER
        )
        self.employer.save()
        
        self.employee = CustomUser.objects.create_user(
            username='employee',
            email='employee@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE
        )
        self.employee.save()
        
        # Create vacancy
        self.vacancy = Vacancy.objects.create(
            employer=self.employer,
            expected_mastery=MasteryOption.ADVANCED
        )

    def test_apply_serialization(self):
        """Test serializing an ApplyVacancy instance"""
        application = ApplyVacancy.objects.create(
            employee=self.employee,
            vacancy=self.vacancy
        )
        
        serializer = ApplySerializer(application)
        self.assertEqual(serializer.data['employee'], self.employee.id)
        self.assertEqual(serializer.data['vacancy'], self.vacancy.id)

    def test_apply_creation(self):
        """Test creating an ApplyVacancy through serializer"""
        data = {
            'employee': self.employee.id,
            'vacancy': self.vacancy.id
        }
        
        serializer = ApplySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        application = serializer.save()
        self.assertEqual(application.employee, self.employee)
        self.assertEqual(application.vacancy, self.vacancy)