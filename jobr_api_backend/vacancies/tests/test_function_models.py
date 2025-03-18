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
        """Test adding and removing skills from a function"""
        # Initially no skills
        self.assertEqual(self.function.skills.count(), 0)

        # Add skills
        self.function.skills.add(self.skill1, self.skill2)
        self.assertEqual(self.function.skills.count(), 2)
        self.assertIn(self.skill1, self.function.skills.all())
        self.assertIn(self.skill2, self.function.skills.all())

        # Add another skill
        self.function.skills.add(self.skill3)
        self.assertEqual(self.function.skills.count(), 3)
        self.assertIn(self.skill3, self.function.skills.all())

        # Remove a skill
        self.function.skills.remove(self.skill2)
        self.assertEqual(self.function.skills.count(), 2)
        self.assertNotIn(self.skill2, self.function.skills.all())

        # Test reverse relationship
        self.assertIn(self.function, self.skill1.functions.all())
        self.assertIn(self.function, self.skill3.functions.all())
        self.assertNotIn(self.function, self.skill2.functions.all())

    def test_function_skills_clear(self):
        """Test clearing all skills from a function"""
        # Add all skills
        self.function.skills.add(self.skill1, self.skill2, self.skill3)
        self.assertEqual(self.function.skills.count(), 3)

        # Clear skills
        self.function.skills.clear()
        self.assertEqual(self.function.skills.count(), 0)

    def test_skill_functions_relationship(self):
        """Test accessing functions from skills"""
        # Create another function
        function2 = Function.objects.create(
            function='Frontend Developer',
            weight=4
        )

        # Add skills to both functions
        self.function.skills.add(self.skill1, self.skill2)
        function2.skills.add(self.skill2, self.skill3)

        # Test skill1 is only in first function
        self.assertEqual(self.skill1.functions.count(), 1)
        self.assertIn(self.function, self.skill1.functions.all())

        # Test skill2 is in both functions
        self.assertEqual(self.skill2.functions.count(), 2)
        self.assertIn(self.function, self.skill2.functions.all())
        self.assertIn(function2, self.skill2.functions.all())

        # Test skill3 is only in second function
        self.assertEqual(self.skill3.functions.count(), 1)
        self.assertIn(function2, self.skill3.functions.all())