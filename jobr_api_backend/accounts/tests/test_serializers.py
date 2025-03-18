from django.test import TestCase
from accounts.models import CustomUser, Employee, Employer, LikedEmployee, ProfileOption
from accounts.serializers import LikedEmployeeSerializer, EmployeeSearchSerializer
from vacancies.models import Skill, Language, Function

class LikedEmployeeSerializerTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create employer user
        self.employer_user = CustomUser.objects.create_user(
            username='employer_test',
            email='employer@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYER
        )
        self.employer = self.employer_user.employer_profile

        # Create employee user
        self.employee_user = CustomUser.objects.create_user(
            username='employee_test',
            email='employee@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE
        )
        self.employee = self.employee_user.employee_profile
        self.employee.city_name = "Test City"
        self.employee.biography = "Test Bio"
        self.employee.save()

        # Create a liked employee instance
        self.liked_employee = LikedEmployee.objects.create(
            employer=self.employer,
            employee=self.employee
        )

    def test_liked_employee_serializer(self):
        """Test LikedEmployeeSerializer"""
        serializer = LikedEmployeeSerializer(self.liked_employee)
        data = serializer.data

        self.assertIn('id', data)
        self.assertIn('employee', data)
        self.assertIn('employee_user', data)
        self.assertIn('created_at', data)

        # Check employee data
        self.assertEqual(data['employee']['city_name'], "Test City")
        self.assertEqual(data['employee']['biography'], "Test Bio")

        # Check employee user data
        self.assertEqual(data['employee_user']['username'], 'employee_test')
        self.assertEqual(data['employee_user']['email'], 'employee@test.com')

class EmployeeSearchSerializerTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create employee user
        self.employee_user = CustomUser.objects.create_user(
            username='employee_test',
            email='employee@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE
        )
        self.employee = self.employee_user.employee_profile
        
        # Add employee details
        self.employee.city_name = "Test City"
        self.employee.biography = "Test Bio"
        self.employee.save()

        # Create some related objects
        self.skill = Skill.objects.create(skill="Test Skill")
        self.language = Language.objects.create(language="Test Language")
        self.function = Function.objects.create(function="Test Function")

        # Add relationships
        self.employee.skill.add(self.skill)
        self.employee.language.add(self.language)
        self.employee.function = self.function
        self.employee.save()

    def test_employee_search_serializer(self):
        """Test EmployeeSearchSerializer"""
        serializer = EmployeeSearchSerializer(self.employee)
        data = serializer.data

        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('city_name', data)
        self.assertIn('biography', data)
        self.assertIn('language', data)
        self.assertIn('skill', data)
        self.assertIn('function', data)

        # Check basic fields
        self.assertEqual(data['city_name'], "Test City")
        self.assertEqual(data['biography'], "Test Bio")

        # Check user data
        self.assertEqual(data['user']['username'], 'employee_test')
        self.assertEqual(data['user']['email'], 'employee@test.com')

        # Check relationships
        self.assertTrue(len(data['skill']) > 0)
        self.assertTrue(len(data['language']) > 0)
        self.assertIsNotNone(data['function'])