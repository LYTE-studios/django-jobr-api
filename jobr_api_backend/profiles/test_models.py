from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import CustomUser, ProfileOption
from profiles.models import Education, WorkExperience, PortfolioItem

class EducationModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for education model tests
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.education_data = {
            'employee': self.user.employee_profile,
            'institution': 'Test University',
            'degree': 'Bachelor',
            'field_of_study': 'Computer Science',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date(),  # Add end date for non-ongoing
            'description': 'Test description',
            'is_ongoing': False
        }

    def test_education_creation(self):
        """
        Test creating an education entry with valid data
        """
        education = Education.objects.create(**self.education_data)
        self.assertEqual(education.institution, 'Test University')
        self.assertEqual(education.degree, 'Bachelor')

    def test_education_dates_validation(self):
        """
        Test education dates validation
        """
        # Test end date before start date
        with self.assertRaises(ValidationError):
            education = Education.objects.create(
                **{**self.education_data, 'end_date': self.education_data['start_date'] - timezone.timedelta(days=1)}
            )

        # Test ongoing education with end date
        with self.assertRaises(ValidationError):
            education = Education.objects.create(
                **{**self.education_data, 'is_ongoing': True}
            )

class WorkExperienceModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for work experience model tests
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.experience_data = {
            'employee': self.user.employee_profile,
            'company_name': 'Test Company',
            'position': 'Software Engineer',
            'description': 'Test description',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date(),  # Add end date for non-current
            'is_current_position': False
        }

    def test_work_experience_creation(self):
        """
        Test creating a work experience entry with valid data
        """
        experience = WorkExperience.objects.create(**self.experience_data)
        self.assertEqual(experience.company_name, 'Test Company')
        self.assertEqual(experience.position, 'Software Engineer')

    def test_work_experience_dates_validation(self):
        """
        Test work experience dates validation
        """
        # Test end date before start date
        with self.assertRaises(ValidationError):
            experience = WorkExperience.objects.create(
                **{**self.experience_data, 'end_date': self.experience_data['start_date'] - timezone.timedelta(days=1)}
            )

        # Test current position with end date
        with self.assertRaises(ValidationError):
            experience = WorkExperience.objects.create(
                **{**self.experience_data, 'is_current_position': True}
            )

class PortfolioItemModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for portfolio item model tests
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.portfolio_data = {
            'employee': self.user.employee_profile,
            'title': 'Test Project',
            'description': 'Test description',
            'date': timezone.now().date(),
            'tags': ['python', 'django'],
            'is_public': True
        }

    def test_portfolio_item_creation(self):
        """
        Test creating a portfolio item with valid data
        """
        portfolio_item = PortfolioItem.objects.create(**self.portfolio_data)
        self.assertEqual(portfolio_item.title, 'Test Project')
        self.assertEqual(portfolio_item.tags, ['python', 'django'])

    def test_portfolio_item_validation(self):
        """
        Test portfolio item validation
        """
        # Test future date
        future_date = timezone.now().date() + timezone.timedelta(days=1)
        with self.assertRaises(ValidationError):
            portfolio_item = PortfolioItem.objects.create(
                **{**self.portfolio_data, 'date': future_date}
            )

        # Test invalid client rating
        with self.assertRaises(ValidationError):
            portfolio_item = PortfolioItem.objects.create(
                **{**self.portfolio_data, 'client_rating': 6.0}
            )

    def test_view_and_like_counts(self):
        """
        Test view and like count functionality
        """
        portfolio_item = PortfolioItem.objects.create(**self.portfolio_data)
        self.assertEqual(portfolio_item.view_count, 0)
        self.assertEqual(portfolio_item.like_count, 0)

        portfolio_item.view_count += 1
        portfolio_item.like_count += 1
        portfolio_item.save()

        self.assertEqual(portfolio_item.view_count, 1)
        self.assertEqual(portfolio_item.like_count, 1)