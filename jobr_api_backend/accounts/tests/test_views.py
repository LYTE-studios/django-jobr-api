from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import CustomUser, Employee, Employer, LikedEmployee, ProfileOption
from vacancies.models import Skill, Language, Function

class EmployeeInteractionTests(TestCase):
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

        # Create another employee for testing
        self.employee_user2 = CustomUser.objects.create_user(
            username='employee_test2',
            email='employee2@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE
        )
        self.employee2 = self.employee_user2.employee_profile

        # Set up test client
        self.client = APIClient()

    def test_like_employee(self):
        """Test liking an employee"""
        self.client.force_authenticate(user=self.employer_user)
        url = reverse('like-employee', kwargs={'employee_id': self.employee.id})
        
        # Test liking
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            LikedEmployee.objects.filter(
                employer=self.employer,
                employee=self.employee
            ).exists()
        )

        # Test duplicate liking
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            LikedEmployee.objects.filter(
                employer=self.employer,
                employee=self.employee
            ).count(),
            1
        )

    def test_unlike_employee(self):
        """Test unliking an employee"""
        self.client.force_authenticate(user=self.employer_user)
        
        # Create a like first
        like = LikedEmployee.objects.create(
            employer=self.employer,
            employee=self.employee
        )
        
        url = reverse('like-employee', kwargs={'employee_id': self.employee.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            LikedEmployee.objects.filter(
                employer=self.employer,
                employee=self.employee
            ).exists()
        )

    def test_like_employee_unauthorized(self):
        """Test that only employers can like employees"""
        self.client.force_authenticate(user=self.employee_user)
        url = reverse('like-employee', kwargs={'employee_id': self.employee2.id})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_liked_employees(self):
        """Test getting list of liked employees"""
        self.client.force_authenticate(user=self.employer_user)
        
        # Create some likes
        LikedEmployee.objects.create(
            employer=self.employer,
            employee=self.employee
        )
        LikedEmployee.objects.create(
            employer=self.employer,
            employee=self.employee2
        )
        
        url = reverse('liked-employees-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)

    def test_search_employees(self):
        """Test searching employees"""
        self.client.force_authenticate(user=self.employer_user)
        url = reverse('employee-search')

        # Test search by term
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

        # Test search by city
        response = self.client.get(url, {'city': 'Test City'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

        # Test search with no results
        response = self.client.get(url, {'search': 'NonexistentTerm'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        # Test search with multiple filters
        skill = Skill.objects.create(skill="Test Skill")
        self.employee.skill.add(skill)
        
        response = self.client.get(url, {
            'search': 'Test',
            'city': 'Test City',
            'skill': skill.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) > 0)
        
        # Verify pagination structure
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)