from django.test import TestCase
from vacancies.models import Function, Skill

class FunctionSkillsTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create function
        self.function = Function.objects.create(
            function='Software Developer',
            weight=5
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

    def test_function_skills_relationship(self):
        """Test assigning skills to a function"""
        # Initially no skills assigned to function
        self.assertEqual(self.function.skills.count(), 0)

        # Assign function to skills
        self.skill1.function = self.function
        self.skill1.save()
        self.skill2.function = self.function
        self.skill2.save()

        # Check skills are assigned
        self.assertEqual(self.function.skills.count(), 2)
        self.assertIn(self.skill1, self.function.skills.all())
        self.assertIn(self.skill2, self.function.skills.all())

        # Check reverse relationship
        self.assertEqual(self.skill1.function, self.function)
        self.assertEqual(self.skill2.function, self.function)

    def test_skill_function_relationship(self):
        """Test accessing function from skills"""
        # Create another function
        function2 = Function.objects.create(
            function='Frontend Developer',
            weight=4
        )

        # Assign functions to skills
        self.skill1.function = self.function
        self.skill1.save()
        self.skill2.function = function2
        self.skill2.save()
        self.skill3.function = function2
        self.skill3.save()

        # Test skill1 is assigned to first function
        self.assertEqual(self.skill1.function, self.function)

        # Test skill2 and skill3 are assigned to second function
        self.assertEqual(self.skill2.function, function2)
        self.assertEqual(self.skill3.function, function2)

        # Test function has correct skills
        self.assertEqual(self.function.skills.count(), 1)
        self.assertEqual(function2.skills.count(), 2)