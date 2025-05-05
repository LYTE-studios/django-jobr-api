from django.test import TestCase
from django.utils import timezone
from accounts.models import CustomUser, ProfileOption
from profiles.models import Education, WorkExperience, PortfolioItem
from profiles.serializers import (
    EducationSerializer,
    WorkExperienceSerializer,
    PortfolioItemSerializer
)
from rest_framework.test import APIRequestFactory

class EducationSerializerTests(TestCase):
    def setUp(self):
        """
        Set up test data for education serializer tests
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.education_data = {
            'institution': 'Test University',
            'degree': 'Bachelor',
            'field_of_study': 'Computer Science',
            'start_date': timezone.now().date().isoformat(),
            'description': 'Test description',
            'is_ongoing': True
        }
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.user

    def test_education_serializer_create(self):
        """
        Test creating education through serializer
        """
        serializer = EducationSerializer(
            data=self.education_data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())
        education = serializer.save()
        self.assertEqual(education.institution, 'Test University')
        self.assertEqual(education.employee, self.user.employee_profile)

    def test_education_serializer_validation(self):
        """
        Test education serializer validation
        """
        # Test invalid dates
        data = self.education_data.copy()
        data['end_date'] = (timezone.now().date() - timezone.timedelta(days=1)).isoformat()
        serializer = EducationSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())

class WorkExperienceSerializerTests(TestCase):
    def setUp(self):
        """
        Set up test data for work experience serializer tests
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.experience_data = {
            'company_name': 'Test Company',
            'position': 'Software Engineer',
            'description': 'Test description',
            'start_date': timezone.now().date().isoformat(),
            'is_current_position': True
        }
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.user

    def test_work_experience_serializer_create(self):
        """
        Test creating work experience through serializer
        """
        serializer = WorkExperienceSerializer(
            data=self.experience_data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())
        experience = serializer.save()
        self.assertEqual(experience.company_name, 'Test Company')
        self.assertEqual(experience.employee, self.user.employee_profile)

    def test_work_experience_serializer_validation(self):
        """
        Test work experience serializer validation
        """
        # Test invalid dates
        data = self.experience_data.copy()
        data['end_date'] = (timezone.now().date() - timezone.timedelta(days=1)).isoformat()
        serializer = WorkExperienceSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())

class PortfolioItemSerializerTests(TestCase):
    def setUp(self):
        """
        Set up test data for portfolio item serializer tests
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.portfolio_data = {
            'title': 'Test Project',
            'description': 'Test description',
            'date': timezone.now().date().isoformat(),
            'tags': ['python', 'django'],
            'is_public': True
        }
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.user

    def test_portfolio_item_serializer_create(self):
        """
        Test creating portfolio item through serializer
        """
        serializer = PortfolioItemSerializer(
            data=self.portfolio_data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())
        portfolio_item = serializer.save()
        self.assertEqual(portfolio_item.title, 'Test Project')
        self.assertEqual(portfolio_item.employee, self.user.employee_profile)

    def test_portfolio_item_serializer_validation(self):
        """
        Test portfolio item serializer validation
        """
        # Test future date
        data = self.portfolio_data.copy()
        data['date'] = (timezone.now().date() + timezone.timedelta(days=1)).isoformat()
        serializer = PortfolioItemSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())

        # Test invalid client rating
        data = self.portfolio_data.copy()
        data['client_rating'] = 6.0
        serializer = PortfolioItemSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())

    def test_read_only_fields(self):
        """
        Test read-only fields are not modifiable
        """
        data = self.portfolio_data.copy()
        data['view_count'] = 10
        data['like_count'] = 5
        
        serializer = PortfolioItemSerializer(
            data=data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())
        portfolio_item = serializer.save()
        
        self.assertEqual(portfolio_item.view_count, 0)
        self.assertEqual(portfolio_item.like_count, 0)