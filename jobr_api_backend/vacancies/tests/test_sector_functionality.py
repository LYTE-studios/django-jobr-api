from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser, ProfileOption
from ..models import Sector, Function

class SectorTests(APITestCase):
    def setUp(self):
        """Set up test data."""
        # Create sectors
        self.tech_sector = Sector.objects.create(name="Technology")
        self.health_sector = Sector.objects.create(name="Healthcare")

        # Create functions
        self.tech_function = Function.objects.create(
            name="Software Developer",
            sector=self.tech_sector
        )
        self.health_function = Function.objects.create(
            name="Nurse",
            sector=self.health_sector
        )
        self.general_function = Function.objects.create(
            name="Manager"  # No sector, available to all
        )

        # Create users with different sectors
        self.tech_user = CustomUser.objects.create_user(
            username="tech@example.com",
            email="tech@example.com",
            password="testpass123",
            role=ProfileOption.EMPLOYEE,
            sector=self.tech_sector
        )

        self.health_user = CustomUser.objects.create_user(
            username="health@example.com",
            email="health@example.com",
            password="testpass123",
            role=ProfileOption.EMPLOYEE,
            sector=self.health_sector
        )

        self.no_sector_user = CustomUser.objects.create_user(
            username="general@example.com",
            email="general@example.com",
            password="testpass123",
            role=ProfileOption.EMPLOYEE
        )

    def test_sector_str_representation(self):
        """Test string representation of Sector model."""
        self.assertEqual(str(self.tech_sector), "Technology")
        self.assertEqual(str(self.health_sector), "Healthcare")

    def test_user_sector_relationship(self):
        """Test relationship between User and Sector."""
        self.assertEqual(self.tech_user.sector, self.tech_sector)
        self.assertEqual(self.health_user.sector, self.health_sector)
        self.assertIsNone(self.no_sector_user.sector)

    def test_functions_view_with_tech_user(self):
        """Test functions view returns only functions from user's sector (tech)."""
        self.client.force_authenticate(user=self.tech_user)
        response = self.client.get(reverse('vacancies:function-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should see tech functions and general functions
        function_names = [f['name'] for f in response.data]
        self.assertIn(self.tech_function.name, function_names)
        self.assertIn(self.general_function.name, function_names)
        self.assertNotIn(self.health_function.name, function_names)

    def test_functions_view_with_health_user(self):
        """Test functions view returns only functions from user's sector (health)."""
        self.client.force_authenticate(user=self.health_user)
        response = self.client.get(reverse('vacancies:function-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should see health functions and general functions
        function_names = [f['name'] for f in response.data]
        self.assertIn(self.health_function.name, function_names)
        self.assertIn(self.general_function.name, function_names)
        self.assertNotIn(self.tech_function.name, function_names)

    def test_functions_view_with_no_sector_user(self):
        """Test functions view returns all functions for user without sector."""
        self.client.force_authenticate(user=self.no_sector_user)
        response = self.client.get(reverse('vacancies:function-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should see all functions
        function_names = [f['name'] for f in response.data]
        self.assertIn(self.tech_function.name, function_names)
        self.assertIn(self.health_function.name, function_names)
        self.assertIn(self.general_function.name, function_names)

    def test_functions_view_unauthenticated(self):
        """Test functions view requires authentication."""
        response = self.client.get(reverse('vacancies:function-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)