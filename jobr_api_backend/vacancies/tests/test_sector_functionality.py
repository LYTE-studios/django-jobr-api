from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import CustomUser, ProfileOption
from vacancies.models import Sector, Function

class SectorTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create sectors
        self.sector1 = Sector.objects.create(
            name='Technology',
            weight=5
        )
        self.sector2 = Sector.objects.create(
            name='Healthcare',
            weight=4
        )

        # Create functions in different sectors
        self.tech_function1 = Function.objects.create(
            function='Software Developer',
            weight=5,
            sector=self.sector1
        )
        self.tech_function2 = Function.objects.create(
            function='Data Scientist',
            weight=4,
            sector=self.sector1
        )
        self.health_function = Function.objects.create(
            function='Nurse',
            weight=5,
            sector=self.sector2
        )

        # Create users in different sectors
        self.tech_user = CustomUser.objects.create_user(
            username='tech_user',
            email='tech@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE,
            sector=self.sector1
        )
        self.health_user = CustomUser.objects.create_user(
            username='health_user',
            email='health@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE,
            sector=self.sector2
        )
        self.no_sector_user = CustomUser.objects.create_user(
            username='no_sector_user',
            email='nosector@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE
        )

        self.client = APIClient()

    def test_sector_str_representation(self):
        """Test string representation of Sector model"""
        self.assertEqual(str(self.sector1), 'Technology at 5')

    def test_function_sector_relationship(self):
        """Test relationship between Function and Sector"""
        tech_functions = Function.objects.filter(sector=self.sector1)
        health_functions = Function.objects.filter(sector=self.sector2)

        self.assertEqual(tech_functions.count(), 2)
        self.assertEqual(health_functions.count(), 1)
        self.assertIn(self.tech_function1, tech_functions)
        self.assertIn(self.tech_function2, tech_functions)
        self.assertIn(self.health_function, health_functions)

    def test_user_sector_relationship(self):
        """Test relationship between User and Sector"""
        tech_users = CustomUser.objects.filter(sector=self.sector1)
        health_users = CustomUser.objects.filter(sector=self.sector2)
        no_sector_users = CustomUser.objects.filter(sector__isnull=True)

        self.assertEqual(tech_users.count(), 1)
        self.assertEqual(health_users.count(), 1)
        self.assertEqual(no_sector_users.count(), 1)
        self.assertIn(self.tech_user, tech_users)
        self.assertIn(self.health_user, health_users)
        self.assertIn(self.no_sector_user, no_sector_users)

    def test_functions_view_with_tech_user(self):
        """Test functions view returns only functions from user's sector (tech)"""
        self.client.force_authenticate(user=self.tech_user)
        response = self.client.get(reverse('functions'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        functions = {func['function'] for func in response.data['results']}
        self.assertEqual(functions, {'Software Developer', 'Data Scientist'})

    def test_functions_view_with_health_user(self):
        """Test functions view returns only functions from user's sector (health)"""
        self.client.force_authenticate(user=self.health_user)
        response = self.client.get(reverse('functions'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['function'], 'Nurse')

    def test_functions_view_with_no_sector_user(self):
        """Test functions view returns all functions for user without sector"""
        self.client.force_authenticate(user=self.no_sector_user)
        response = self.client.get(reverse('functions'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        functions = {func['function'] for func in response.data['results']}
        self.assertEqual(functions, {'Software Developer', 'Data Scientist', 'Nurse'})

    def test_functions_view_unauthenticated(self):
        """Test functions view requires authentication"""
        response = self.client.get(reverse('functions'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)