from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser, ProfileOption
from ..models import Function, Skill

class SkillsViewTests(APITestCase):
    def setUp(self):
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123",
            role=ProfileOption.EMPLOYER
        )

        # Create functions
        self.function1 = Function.objects.create(name="Software Development")
        self.function2 = Function.objects.create(name="Project Management")

        # Create skills for function1
        self.skill1 = Skill.objects.create(name="Python")
        self.skill2 = Skill.objects.create(name="JavaScript")
        self.skill3 = Skill.objects.create(name="SQL")

        # Create skills for function2
        self.skill4 = Skill.objects.create(name="Agile")
        self.skill5 = Skill.objects.create(name="Scrum")

        # Associate skills with functions
        self.function1.skills.add(self.skill1, self.skill2, self.skill3)
        self.function2.skills.add(self.skill4, self.skill5)

        self.client.force_authenticate(user=self.user)

    def test_get_all_skills(self):
        """Test getting all skills without function filter."""
        url = reverse('vacancies:skill-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)  # All skills

    def test_get_skills_by_function(self):
        """Test getting skills filtered by function."""
        url = f"{reverse('vacancies:skill-list')}?function={self.function1.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # Only function1 skills
        skill_names = [skill['name'] for skill in response.data]
        self.assertIn('Python', skill_names)
        self.assertIn('JavaScript', skill_names)
        self.assertIn('SQL', skill_names)

    def test_get_skills_by_different_function(self):
        """Test getting skills for a different function."""
        url = f"{reverse('vacancies:skill-list')}?function={self.function2.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only function2 skills
        skill_names = [skill['name'] for skill in response.data]
        self.assertIn('Agile', skill_names)
        self.assertIn('Scrum', skill_names)

    def test_get_skills_nonexistent_function(self):
        """Test getting skills for a nonexistent function."""
        url = f"{reverse('vacancies:skill-list')}?function=999"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No skills found

    def test_unauthenticated_access(self):
        """Test that unauthenticated access is not allowed."""
        self.client.force_authenticate(user=None)
        url = reverse('vacancies:skill-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)