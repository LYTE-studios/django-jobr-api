from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import CustomUser, Employee, Employer, ProfileOption, Function, Skill, Language

class SearchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test data
        self.function = Function.objects.create(name='Software Developer')
        self.skill = Skill.objects.create(name='Python')
        self.language = Language.objects.create(name='English')

        # Create a searching user (employer)
        self.user = CustomUser.objects.create_user(
            username='searcher',
            email='searcher@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        self.client.force_authenticate(user=self.user)
        self.user.employer_profile.company_name = 'Search Corp'
        self.user.employer_profile.city = 'Brussels'
        self.user.employer_profile.save()

        # Create an employee to search for
        self.employee = CustomUser.objects.create_user(
            username='employee1',
            email='employee1@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.employee.employee_profile.biography = 'Experienced software developer'
        self.employee.employee_profile.city_name = 'Brussels'
        self.employee.employee_profile.function = self.function
        self.employee.employee_profile.save()
        self.employee.employee_profile.skill.add(self.skill)
        self.employee.employee_profile.language.add(self.language)

        # Create an employer to search for
        self.employer = CustomUser.objects.create_user(
            username='employer1',
            email='employer1@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        self.employer.employer_profile.company_name = 'Tech Corp'
        self.employer.employer_profile.biography = 'Leading tech company'
        self.employer.employer_profile.city = 'Antwerp'
        self.employer.employer_profile.website = 'https://techcorp.com'
        self.employer.employer_profile.vat_number = 'BE0123456789'
        self.employer.employer_profile.save()

    def test_employee_search_by_username(self):
        """Test searching employees by username."""
        url = reverse('employee-search')
        response = self.client.get(f"{url}?search=employee1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'employee1')

    def test_employee_search_by_biography(self):
        """Test searching employees by biography."""
        url = reverse('employee-search')
        response = self.client.get(f"{url}?search=software")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['biography'], 'Experienced software developer')

    def test_employee_search_by_city(self):
        """Test searching employees by city."""
        url = reverse('employee-search')
        response = self.client.get(f"{url}?search=Brussels")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['city'], 'Brussels')

    def test_employee_search_by_skill(self):
        """Test searching employees by skill."""
        url = reverse('employee-search')
        response = self.client.get(f"{url}?search=Python")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(any(skill['name'] == 'Python' for skill in response.data[0]['skill']))

    def test_employer_search_by_company_name(self):
        """Test searching employers by company name."""
        url = reverse('employer-search')
        response = self.client.get(f"{url}?search=Tech")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company_name'], 'Tech Corp')

    def test_employer_search_by_city(self):
        """Test searching employers by city."""
        url = reverse('employer-search')
        response = self.client.get(f"{url}?search=Antwerp")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['city'], 'Antwerp')

    def test_employer_search_by_vat(self):
        """Test searching employers by VAT number."""
        url = reverse('employer-search')
        response = self.client.get(f"{url}?search=BE012")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['vat_number'], 'BE0123456789')

    def test_search_no_results(self):
        """Test search with no matching results."""
        url = reverse('employee-search')
        response = self.client.get(f"{url}?search=nonexistent")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_empty_term(self):
        """Test search with empty search term returns all results."""
        url = reverse('employee-search')
        response = self.client.get(f"{url}?search=")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one employee in the database