from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from vacancies.models import Function, Skill
from accounts.models import CustomUser

class SkillsViewTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test user and authenticate
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create functions
        self.function1 = Function.objects.create(
            function='Software Developer',
            weight=5
        )
        self.function2 = Function.objects.create(
            function='Frontend Developer',
            weight=4
        )

        # Create skills
        self.skill1 = Skill.objects.create(
            skill='Python',
            category='hard',
            weight=5
        )
        self.skill2 = Skill.objects.create(
            skill='JavaScript',
            category='hard',
            weight=4
        )
        self.skill3 = Skill.objects.create(
            skill='Communication',
            category='soft',
            weight=3
        )

        # Associate skills with functions
        self.skill1.function = self.function1
        self.skill1.save()
        self.skill2.function = self.function2  # Changed from function1 to function2
        self.skill2.save()
        self.skill3.function = self.function2
        self.skill3.save()

    def test_get_all_skills(self):
        """Test getting all skills without function filter"""
        url = reverse('skills')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        skills = {skill['skill'] for skill in response.data}
        self.assertEqual(skills, {'Python', 'JavaScript', 'Communication'})

    def test_get_skills_by_function(self):
        """Test getting skills filtered by function"""
        url = f"{reverse('skills')}?function_id={self.function1.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        skills = {skill['skill'] for skill in response.data}
        self.assertEqual(skills, {'Python'})

    def test_get_skills_by_different_function(self):
        """Test getting skills for a different function"""
        url = f"{reverse('skills')}?function_id={self.function2.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        skills = {skill['skill'] for skill in response.data}
        self.assertEqual(skills, {'JavaScript', 'Communication'})

    def test_get_skills_nonexistent_function(self):
        """Test getting skills for a nonexistent function"""
        url = f"{reverse('skills')}?function_id=999"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Function not found.')

    def test_unauthenticated_access(self):
        """Test that unauthenticated access is not allowed"""
        # Create a new client without authentication
        client = APIClient()
        url = reverse('skills')
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)