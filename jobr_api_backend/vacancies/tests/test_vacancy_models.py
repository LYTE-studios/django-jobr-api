from django.test import TestCase
from django.contrib.auth import get_user_model
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
    Weekday,
    SalaryBenefit
)
from decimal import Decimal
from django.utils import timezone

User = get_user_model()

class VacancyModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for Vacancy model tests
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
        self.weekday = Weekday.objects.create(name='Monday')
        self.skill = Skill.objects.create(skill='Python', category='hard', weight=5)
        self.salary_benefit = SalaryBenefit.objects.create(name='Health Insurance', weight=3)
        
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
        self.vacancy.week_day.add(self.weekday)
        self.vacancy.salary_benefits.add(self.salary_benefit)

    def test_vacancy_creation(self):
        """
        Test creating a Vacancy instance with all fields
        """
        # Test basic fields
        self.assertEqual(self.vacancy.employer, self.employer)
        self.assertEqual(self.vacancy.expected_mastery, MasteryOption.ADVANCED)
        self.assertEqual(self.vacancy.location, self.location)
        self.assertEqual(self.vacancy.function, self.function)
        self.assertEqual(self.vacancy.salary, Decimal('50000.00'))
        
        # Test many-to-many relationships
        self.assertEqual(self.vacancy.contract_type.count(), 1)
        self.assertEqual(self.vacancy.skill.count(), 1)
        self.assertEqual(self.vacancy.week_day.count(), 1)
        self.assertEqual(self.vacancy.salary_benefits.count(), 1)
        
        self.assertIn(self.contract_type, self.vacancy.contract_type.all())
        self.assertIn(self.skill, self.vacancy.skill.all())
        self.assertIn(self.weekday, self.vacancy.week_day.all())
        self.assertIn(self.salary_benefit, self.vacancy.salary_benefits.all())
        
        # Test reverse relationships
        self.assertIn(self.vacancy, self.contract_type.vacancy_set.all())
        self.assertIn(self.vacancy, self.skill.vacancy_set.all())
        self.assertIn(self.vacancy, self.weekday.vacancy_set.all())
        self.assertIn(self.vacancy, self.salary_benefit.vacancy_set.all())

    def test_salary_benefits(self):
        """
        Test salary benefits functionality
        """
        # Create additional salary benefits
        benefit2 = SalaryBenefit.objects.create(name='Company Car', weight=4)
        benefit3 = SalaryBenefit.objects.create(name='Meal Vouchers', weight=2)

        # Add multiple benefits
        self.vacancy.salary_benefits.add(benefit2, benefit3)

        # Test that all benefits are present
        self.assertEqual(self.vacancy.salary_benefits.count(), 3)
        self.assertIn(self.salary_benefit, self.vacancy.salary_benefits.all())
        self.assertIn(benefit2, self.vacancy.salary_benefits.all())
        self.assertIn(benefit3, self.vacancy.salary_benefits.all())

        # Test removing a benefit
        self.vacancy.salary_benefits.remove(benefit2)
        self.assertEqual(self.vacancy.salary_benefits.count(), 2)
        self.assertNotIn(benefit2, self.vacancy.salary_benefits.all())

        # Test clearing all benefits
        self.vacancy.salary_benefits.clear()
        self.assertEqual(self.vacancy.salary_benefits.count(), 0)

    def test_vacancy_optional_fields(self):
        """
        Test Vacancy creation with optional fields
        """
        vacancy = Vacancy.objects.create(
            employer=self.employer
        )
        
        self.assertIsNone(vacancy.expected_mastery)
        self.assertIsNone(vacancy.location)
        self.assertIsNone(vacancy.function)
        self.assertIsNone(vacancy.job_date)
        self.assertIsNone(vacancy.salary)

class VacancyLanguageTests(TestCase):
    def setUp(self):
        """
        Set up test data for VacancyLanguage model tests
        """
        self.language = Language.objects.create(language='English', weight=5)
        self.vacancy_language = VacancyLanguage.objects.create(
            language=self.language,
            mastery=MasteryOption.ADVANCED
        )

    def test_vacancy_language_creation(self):
        """
        Test creating a VacancyLanguage instance
        """
        self.assertEqual(self.vacancy_language.language, self.language)
        self.assertEqual(self.vacancy_language.mastery, MasteryOption.ADVANCED)

class VacancyDescriptionTests(TestCase):
    def setUp(self):
        """
        Set up test data for VacancyDescription model tests
        """
        self.question = Question.objects.create(question='Experience?', weight=1)
        self.description = VacancyDescription.objects.create(
            question=self.question,
            description="Test description"
        )

    def test_vacancy_description_creation(self):
        """
        Test creating a VacancyDescription instance
        """
        self.assertEqual(self.description.question, self.question)
        self.assertEqual(self.description.description, "Test description")

    def test_main_description(self):
        """
        Test creating a main description (no question)
        """
        main_desc = VacancyDescription.objects.create(
            description="Main description"
        )
        self.assertIsNone(main_desc.question)
        self.assertEqual(main_desc.description, "Main description")

class ApplyVacancyModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for ApplyVacancy model tests
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

    def test_apply_vacancy_creation(self):
        """
        Test creating an ApplyVacancy instance
        """
        application = ApplyVacancy.objects.create(
            employee=self.employee,
            vacancy=self.vacancy
        )
        
        self.assertEqual(application.employee, self.employee)
        self.assertEqual(application.vacancy, self.vacancy)

    def test_multiple_applications(self):
        """
        Test multiple applications for the same vacancy
        """
        # Create another employee
        employee2 = CustomUser.objects.create_user(
            username='employee2',
            email='employee2@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE
        )
        employee2.save()  # Save to ensure employee_profile is created
        
        # Both employees apply to the vacancy
        application1 = ApplyVacancy.objects.create(
            employee=self.employee,
            vacancy=self.vacancy
        )
        application2 = ApplyVacancy.objects.create(
            employee=employee2,
            vacancy=self.vacancy
        )
        
        # Verify both applications exist
        applications = ApplyVacancy.objects.filter(vacancy=self.vacancy)
        self.assertEqual(applications.count(), 2)
        self.assertIn(application1, applications)
        self.assertIn(application2, applications)

    def test_cascade_delete(self):
        """
        Test that applications are deleted when vacancy is deleted
        """
        application = ApplyVacancy.objects.create(
            employee=self.employee,
            vacancy=self.vacancy
        )
        
        # Delete vacancy and verify application is deleted
        self.vacancy.delete()
        with self.assertRaises(ApplyVacancy.DoesNotExist):
            ApplyVacancy.objects.get(id=application.id)