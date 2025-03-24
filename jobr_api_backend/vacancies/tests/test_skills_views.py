from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser, ProfileOption
from vacancies.models import Function, Skill, FunctionSkill

class SkillsViewTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            role=ProfileOption.EMPLOYER
        )
        
        # Create functions
        self.function1 = Function.objects.create(
            function='Developer',
            weight=4
        )
        self.function2 = Function.objects.create(
            function='Designer',
            weight=3
        )
        
        # Create skills
        self.skill1 = Skill.objects.create(
            skill='Python',
            category='hard'
        )
        self.skill2 = Skill.objects.create(
            skill='JavaScript',
            category='hard'
        )
        self.skill3 = Skill.objects.create(
            skill='UI Design',
            category='hard'
        )
        
        # Create function-skill relationships with weights
        FunctionSkill.objects.create(
            function=self.function1,
            skill=self.skill1,
            weight=8
        )
        FunctionSkill.objects.create(
            function=self.function1,
            skill=self.skill2,
            weight=6
        )
        FunctionSkill.objects.create(
            function=self.function2,
            skill=self.skill3,
            weight=9
        )
        
        # Set up client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_all_skills(self):
        """Test getting all skills without function filter"""
        url = reverse('skills')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        skills = {skill['skill'] for skill in response.data}
        self.assertEqual(skills, {'Python', 'JavaScript', 'UI Design'})

    def test_get_skills_by_function(self):
        """Test getting skills filtered by function"""
        url = f"{reverse('skills')}?function={self.function1.id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        skills = {skill['skill'] for skill in response.data}
        self.assertEqual(skills, {'Python', 'JavaScript'})

    def test_get_skills_by_different_function(self):
        """Test getting skills for a different function"""
        url = f"{reverse('skills')}?function={self.function2.id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['skill'], 'UI Design')

    def test_get_skills_nonexistent_function(self):
        """Test getting skills for a nonexistent function"""
        url = f"{reverse('skills')}?function=999"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_unauthenticated_access(self):
        """Test that unauthenticated access is not allowed"""
        self.client.logout()
        url = reverse('skills')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)