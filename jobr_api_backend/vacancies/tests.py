from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta

from .models import (
    Vacancy, 
    ContractType, 
    Function, 
    Location, 
    Skill, 
    Language, 
    VacancyLanguage, 
    VacancyDescription, 
    VacancyQuestion, 
    Weekday
)
from accounts.models import CustomUser, Employer, ProfileOption

User = get_user_model()

class VacancyTests(APITestCase):
    def setUp(self):
        # Create a test employer
        self.user = CustomUser.objects.create_user(
            username="testemployer", 
            email="employer@example.com", 
            password="testpass",
            role=ProfileOption.EMPLOYER
        )
        
        # Refresh the user to ensure the employer_profile is created
        self.user.refresh_from_db()

        # Create supporting models
        self.contract_type = ContractType.objects.create(contract_type="Full-time")
        self.function = Function.objects.create(function="Software Development")
        self.location = Location.objects.create(location="New York")
        self.skill = Skill.objects.create(skill="Python", category="hard")
        self.language = Language.objects.create(language="English")
        self.weekday = Weekday.objects.create(name="Monday")

        # Authenticate the employer
        self.client.force_authenticate(user=self.user)

    def test_create_vacancy_full_details(self):
        """
        Test creating a vacancy with all possible details
        """
        vacancy_data = {
            "expected_mastery": "Intermediate",
            "contract_type": [{"id": self.contract_type.id}],
            "location": {"id": self.location.id},
            "function": {"id": self.function.id},
            "week_day": [{"name": self.weekday.name}],
            "job_date": str(date.today() + timedelta(days=30)),
            "salary": "50000.00",
            "skill": [{"id": self.skill.id}],
            "languages": [
                {
                    "language": self.language.id,
                    "mastery": "Intermediate"
                }
            ],
            "descriptions": [],
            "questions": [
                {"question": "Are you available for full-time work?"}
            ]
        }

        url = reverse('vacancy-list')
        response = self.client.post(url, vacancy_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify vacancy was created with correct details
        vacancy = Vacancy.objects.get(id=response.data['id'])
        self.assertEqual(vacancy.employer, self.user)
        self.assertEqual(vacancy.expected_mastery, "Intermediate")
        self.assertEqual(vacancy.location, self.location)
        self.assertEqual(vacancy.function, self.function)
        self.assertTrue(self.contract_type in vacancy.contract_type.all())
        self.assertTrue(self.skill in vacancy.skill.all())

    def test_update_vacancy(self):
        """
        Test updating an existing vacancy
        """
        # First create a vacancy
        initial_vacancy = Vacancy.objects.create(
            employer=self.user,
            expected_mastery="Beginner",
            location=self.location,
            function=self.function
        )
        initial_vacancy.contract_type.add(self.contract_type)
        initial_vacancy.skill.add(self.skill)

        # Prepare update data
        update_data = {
            "expected_mastery": "Advanced",
            "contract_type": [{"id": self.contract_type.id}],
            "location": {"id": self.location.id},
            "function": {"id": self.function.id},
            "salary": "75000.00",
            "skill": [{"id": self.skill.id}]
        }

        url = reverse('vacancy-detail', kwargs={'pk': initial_vacancy.id})
        response = self.client.put(url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh vacancy from database
        updated_vacancy = Vacancy.objects.get(id=initial_vacancy.id)
        self.assertEqual(updated_vacancy.expected_mastery, "Advanced")
        self.assertEqual(float(updated_vacancy.salary), 75000.00)
        self.assertTrue(self.contract_type in updated_vacancy.contract_type.all())

    def test_vacancy_validation(self):
        """
        Test vacancy creation with invalid data
        """
        invalid_vacancy_data = {
            "expected_mastery": "Invalid Mastery",  # Invalid mastery level
            "contract_type": [{"id": 9999}],  # Non-existent contract type
        }

        url = reverse('vacancy-list')
        response = self.client.post(url, invalid_vacancy_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
