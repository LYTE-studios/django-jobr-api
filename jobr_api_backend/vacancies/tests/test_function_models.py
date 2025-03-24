from django.test import TestCase
from vacancies.models import Function, Skill, FunctionSkill

class FunctionSkillsTests(TestCase):
    def setUp(self):
        """Set up test data"""
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

    def test_function_skills_relationship(self):
        """Test assigning skills to a function with weights"""
        # Create function-skill relationships
        fs1 = FunctionSkill.objects.create(
            function=self.function1,
            skill=self.skill1,
            weight=8
        )
        fs2 = FunctionSkill.objects.create(
            function=self.function1,
            skill=self.skill2,
            weight=6
        )
        
        # Test relationships from function perspective
        function_skills = self.function1.functionskill_set.all().order_by('-weight')
        self.assertEqual(len(function_skills), 2)
        self.assertEqual(function_skills[0].skill, self.skill1)
        self.assertEqual(function_skills[0].weight, 8)
        self.assertEqual(function_skills[1].skill, self.skill2)
        self.assertEqual(function_skills[1].weight, 6)
        
        # Test that skills are accessible through the many-to-many relationship
        skills = self.function1.skills.all()
        self.assertEqual(len(skills), 2)
        self.assertIn(self.skill1, skills)
        self.assertIn(self.skill2, skills)

    def test_skill_function_relationship(self):
        """Test accessing functions from skills with weights"""
        # Create function-skill relationships
        fs1 = FunctionSkill.objects.create(
            function=self.function1,
            skill=self.skill1,
            weight=8
        )
        fs2 = FunctionSkill.objects.create(
            function=self.function2,
            skill=self.skill1,
            weight=4
        )
        
        # Test relationships from skill perspective
        skill_functions = self.skill1.functionskill_set.all().order_by('-weight')
        self.assertEqual(len(skill_functions), 2)
        self.assertEqual(skill_functions[0].function, self.function1)
        self.assertEqual(skill_functions[0].weight, 8)
        self.assertEqual(skill_functions[1].function, self.function2)
        self.assertEqual(skill_functions[1].weight, 4)
        
        # Test that functions are accessible through the many-to-many relationship
        functions = self.skill1.functions.all()
        self.assertEqual(len(functions), 2)
        self.assertIn(self.function1, functions)
        self.assertIn(self.function2, functions)

    def test_function_skill_weight_ordering(self):
        """Test that skills are ordered by weight within a function"""
        # Create multiple skills with different weights
        FunctionSkill.objects.create(
            function=self.function1,
            skill=self.skill1,
            weight=8  # Highest weight
        )
        FunctionSkill.objects.create(
            function=self.function1,
            skill=self.skill2,
            weight=6  # Medium weight
        )
        FunctionSkill.objects.create(
            function=self.function1,
            skill=self.skill3,
            weight=4  # Lowest weight
        )
        
        # Get skills ordered by weight
        function_skills = FunctionSkill.objects.filter(
            function=self.function1
        ).order_by('-weight')
        
        # Verify order
        self.assertEqual(function_skills[0].skill, self.skill1)  # Weight 8
        self.assertEqual(function_skills[1].skill, self.skill2)  # Weight 6
        self.assertEqual(function_skills[2].skill, self.skill3)  # Weight 4

    def test_function_skill_unique_constraint(self):
        """Test that a skill can't be added to a function twice"""
        # Create first relationship
        FunctionSkill.objects.create(
            function=self.function1,
            skill=self.skill1,
            weight=8
        )
        
        # Attempt to create duplicate relationship
        with self.assertRaises(Exception):
            FunctionSkill.objects.create(
                function=self.function1,
                skill=self.skill1,
                weight=6
            )