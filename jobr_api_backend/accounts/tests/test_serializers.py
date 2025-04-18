from django.test import TestCase
from accounts.models import (
    CustomUser, Employee, LikedEmployee, ProfileOption,
    UserGallery
)
from accounts.serializers import (
    LikedEmployeeSerializer, EmployeeSearchSerializer, UserSerializer
)
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
        self.assertIn('user', data)
        self.assertIn('created_at', data)

        # Check user data
        self.assertEqual(data['user']['username'], 'employee_test')
        self.assertEqual(data['user']['email'], 'employee@test.com')
        self.assertEqual(data['user']['role'], ProfileOption.EMPLOYEE)

        # Check employee profile data in user
        employee_profile = data['user']['employee_profile']
        self.assertIsNotNone(employee_profile)
        self.assertEqual(employee_profile['city_name'], "Test City")
        self.assertEqual(employee_profile['biography'], "Test Bio")

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
        self.skill = Skill.objects.create(name="Test Skill")
        self.language = Language.objects.create(name="Test Language")
        self.function = Function.objects.create(name="Test Function")

        # Add relationships
        self.employee.skill.add(self.skill)
        self.employee.language.add(self.language)
        self.employee.function = self.function
        self.employee.save()

    def test_employee_search_serializer(self):
        """Test EmployeeSearchSerializer"""
        serializer = EmployeeSearchSerializer(self.employee)
        data = serializer.data

        self.assertIn('user', data)
        user_data = data['user']

        # Check user basic data
        self.assertEqual(user_data['username'], 'employee_test')
        self.assertEqual(user_data['email'], 'employee@test.com')
        self.assertEqual(user_data['role'], ProfileOption.EMPLOYEE)

        # Check employee profile data
        employee_profile = user_data['employee_profile']
        self.assertIsNotNone(employee_profile)
        self.assertEqual(employee_profile['city_name'], "Test City")
        self.assertEqual(employee_profile['biography'], "Test Bio")

        # Check relationships in employee profile
        self.assertTrue(len(employee_profile['skill']) > 0)
        self.assertTrue(len(employee_profile['language']) > 0)
        self.assertIsNotNone(employee_profile['function'])

class UserSerializerTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            username='test_user',
            email='test@test.com',
            password='testpass'
        )

    def test_user_without_profile(self):
        """Test serializing user without any profile"""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertIsNone(data['employee_profile'])
        self.assertIsNone(data['employer_profile'])
        self.assertEqual(len(data['user_gallery']), 0)

    def test_user_with_gallery(self):
        """Test serializing user with gallery images"""
        # Create temporary image file
        import tempfile
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            image = Image.new('RGB', (100, 100), color='red')
            image.save(temp_file.name)
            
            # Create gallery entries
            with open(temp_file.name, 'rb') as img:
                gallery1 = UserGallery.objects.create(
                    user=self.user,
                    gallery=SimpleUploadedFile(
                        name='test_gallery1.png',
                        content=img.read(),
                        content_type='image/png'
                    )
                )
            with open(temp_file.name, 'rb') as img:
                gallery2 = UserGallery.objects.create(
                    user=self.user,
                    gallery=SimpleUploadedFile(
                        name='test_gallery2.png',
                        content=img.read(),
                        content_type='image/png'
                    )
                )

        # Test serializer output
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertEqual(len(data['user_gallery']), 2)
        self.assertEqual(data['user_gallery'][0]['id'], gallery1.id)
        self.assertEqual(data['user_gallery'][1]['id'], gallery2.id)
        self.assertTrue(data['user_gallery'][0]['gallery'])
        self.assertTrue(data['user_gallery'][1]['gallery'])

    def test_employee_profile_creation(self):
        """Test creating employee profile"""
        self.user.role = ProfileOption.EMPLOYEE
        employee_data = {
            'employee_profile': {
                'city_name': 'Test City',
                'biography': 'Test Bio'
            }
        }

        serializer = UserSerializer(self.user, data=employee_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertIsNotNone(updated_user.employee_profile)
        self.assertEqual(updated_user.employee_profile.city_name, 'Test City')
        self.assertEqual(updated_user.employee_profile.biography, 'Test Bio')
        self.assertIsNone(updated_user.employer_profile)

    def test_employer_profile_creation(self):
        """Test creating employer profile"""
        self.user.role = ProfileOption.EMPLOYER
        employer_data = {
            'employer_profile': {
                'company_name': 'Test Company',
                'city': 'Test City'
            }
        }

        serializer = UserSerializer(self.user, data=employer_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertIsNotNone(updated_user.employer_profile)
        self.assertEqual(updated_user.employer_profile.company_name, 'Test Company')
        self.assertEqual(updated_user.employer_profile.city, 'Test City')
        self.assertIsNone(updated_user.employee_profile)

    def test_profile_switch(self):
        """Test switching from employee to employer profile"""
        # First create employee profile
        self.user.role = ProfileOption.EMPLOYEE
        employee_data = {
            'employee_profile': {
                'city_name': 'Test City',
                'biography': 'Test Bio'
            }
        }
        serializer = UserSerializer(self.user, data=employee_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertIsNotNone(updated_user.employee_profile)

        # Switch to employer
        updated_user.role = ProfileOption.EMPLOYER
        employer_data = {
            'employer_profile': {
                'company_name': 'Test Company',
                'city': 'Test City'
            }
        }
        serializer = UserSerializer(updated_user, data=employer_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        # Check that employee profile is gone and employer profile exists
        self.assertIsNone(updated_user.employee_profile)
        self.assertIsNotNone(updated_user.employer_profile)
        self.assertEqual(updated_user.employer_profile.company_name, 'Test Company')

from accounts.models import Company

class CompanySerializerTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.company_data = {
            'name': 'Test Company',
            'vat_number': 'BE0123456789',
            'street_name': 'Test Street',
            'house_number': '123',
            'city': 'Test City',
            'postal_code': '1000',
            'website': 'https://test.com',
            'description': 'Test Description'
        }
        self.company = Company.objects.create(**self.company_data)

    def test_partial_update(self):
        """Test that partial updates don't affect other fields"""
        from accounts.serializers import CompanySerializer
        
        update_data = {
            'name': 'Updated Company',
            'website': 'https://updated.com'
        }
        
        serializer = CompanySerializer(self.company, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_company = serializer.save()
        
        # Check updated fields
        self.assertEqual(updated_company.name, 'Updated Company')
        self.assertEqual(updated_company.website, 'https://updated.com')
        
        # Check unchanged fields
        self.assertEqual(updated_company.vat_number, self.company_data['vat_number'])
        self.assertEqual(updated_company.street_name, self.company_data['street_name'])
        self.assertEqual(updated_company.house_number, self.company_data['house_number'])
        self.assertEqual(updated_company.city, self.company_data['city'])
        self.assertEqual(updated_company.postal_code, self.company_data['postal_code'])
        self.assertEqual(updated_company.description, self.company_data['description'])

    def test_null_values_update(self):
        """Test that fields can be set to null during update"""
        from accounts.serializers import CompanySerializer
        
        update_data = {
            'website': None,
            'description': None
        }
        
        serializer = CompanySerializer(self.company, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_company = serializer.save()
        
        # Check nullified fields
        self.assertIsNone(updated_company.website)
        self.assertIsNone(updated_company.description)
        
        # Check unchanged fields
        self.assertEqual(updated_company.name, self.company_data['name'])
        self.assertEqual(updated_company.vat_number, self.company_data['vat_number'])

    def test_optional_fields_update(self):
        """Test that fields are optional during updates"""
        from accounts.serializers import CompanySerializer
        
        # Empty update should be valid
        serializer = CompanySerializer(self.company, data={}, partial=True)
        self.assertTrue(serializer.is_valid())
        
        # Update with only one field should be valid
        serializer = CompanySerializer(self.company, data={'name': 'New Name'}, partial=True)
        self.assertTrue(serializer.is_valid())