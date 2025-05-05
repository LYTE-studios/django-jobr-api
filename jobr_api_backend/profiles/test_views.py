from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from accounts.models import CustomUser, ProfileOption
from profiles.models import Education, WorkExperience, PortfolioItem

class EducationViewSetTests(APITestCase):
    def setUp(self):
        """
        Set up test data for education view tests
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.education_data = {
            'institution': 'Test University',
            'degree': 'Bachelor',
            'field_of_study': 'Computer Science',
            'start_date': timezone.now().date().isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'description': 'Test description',
            'is_ongoing': False
        }

    def test_create_education(self):
        """
        Test creating an education entry
        """
        url = reverse('education-list')
        response = self.client.post(url, self.education_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Education.objects.count(), 1)
        self.assertEqual(Education.objects.get().institution, 'Test University')

    def test_list_education(self):
        """
        Test listing education entries
        """
        Education.objects.create(
            employee=self.user.employee_profile,
            **{**self.education_data, 'start_date': timezone.now().date(), 'end_date': timezone.now().date()}
        )
        url = reverse('education-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

    def test_update_education(self):
        """
        Test updating an education entry
        """
        education = Education.objects.create(
            employee=self.user.employee_profile,
            **{**self.education_data, 'start_date': timezone.now().date(), 'end_date': timezone.now().date()}
        )
        url = reverse('education-detail', kwargs={'pk': education.pk})
        update_data = {
            'institution': 'Updated University',
            'degree': 'Master',
            'field_of_study': 'Computer Science',
            'start_date': timezone.now().date().isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'description': 'Updated description',
            'is_ongoing': False
        }
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Education.objects.get().institution, 'Updated University')

class WorkExperienceViewSetTests(APITestCase):
    def setUp(self):
        """
        Set up test data for work experience view tests
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.experience_data = {
            'company_name': 'Test Company',
            'position': 'Software Engineer',
            'description': 'Test description',
            'start_date': timezone.now().date().isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'is_current_position': False
        }

    def test_create_experience(self):
        """
        Test creating a work experience entry
        """
        url = reverse('experience-list')
        response = self.client.post(url, self.experience_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkExperience.objects.count(), 1)
        self.assertEqual(WorkExperience.objects.get().company_name, 'Test Company')

    def test_list_experience(self):
        """
        Test listing work experience entries
        """
        WorkExperience.objects.create(
            employee=self.user.employee_profile,
            **{**self.experience_data, 'start_date': timezone.now().date(), 'end_date': timezone.now().date()}
        )
        url = reverse('experience-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

class PortfolioViewSetTests(APITestCase):
    def setUp(self):
        """
        Set up test data for portfolio view tests
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.portfolio_data = {
            'title': 'Test Project',
            'description': 'Test description',
            'date': timezone.now().date().isoformat(),
            'tags': ['python', 'django'],
            'is_public': True
        }

    def test_create_portfolio_item(self):
        """
        Test creating a portfolio item
        """
        url = reverse('portfolio-list')
        response = self.client.post(url, self.portfolio_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PortfolioItem.objects.count(), 1)
        self.assertEqual(PortfolioItem.objects.get().title, 'Test Project')

    def test_increment_view_count(self):
        """
        Test incrementing view count
        """
        portfolio_item = PortfolioItem.objects.create(
            employee=self.user.employee_profile,
            **{**self.portfolio_data, 'date': timezone.now().date()}
        )
        url = reverse('portfolio-increment-view', kwargs={'pk': portfolio_item.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PortfolioItem.objects.get().view_count, 1)

    def test_toggle_like(self):
        """
        Test toggling like
        """
        portfolio_item = PortfolioItem.objects.create(
            employee=self.user.employee_profile,
            **{**self.portfolio_data, 'date': timezone.now().date()}
        )
        url = reverse('portfolio-toggle-like', kwargs={'pk': portfolio_item.pk})
        response = self.client.post(url, {'liked': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PortfolioItem.objects.get().like_count, 1)

    def test_trending_portfolio_items(self):
        """
        Test getting trending portfolio items
        """
        # Create some portfolio items with different view/like counts
        for i in range(3):
            PortfolioItem.objects.create(
                employee=self.user.employee_profile,
                title=f'Project {i}',
                description='Test',
                date=timezone.now().date(),
                view_count=i,
                like_count=i
            )

        url = reverse('portfolio-trending')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['results']), 3)
        # Check if ordered by view_count and like_count
        self.assertEqual(response.data['results'][0]['title'], 'Project 2')