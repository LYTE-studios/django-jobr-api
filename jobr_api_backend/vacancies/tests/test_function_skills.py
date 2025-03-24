from django.test import TestCase
from ..models import Function, Skill, FunctionSkill, Sector

class FunctionSkillTests(TestCase):
    def setUp(self):
        # Create a sector
        self.sector = Sector.objects.create(
            name="Hospitality",
            weight=1
        )

        # Create functions
        self.bartending = Function.objects.create(
            function="Bartending",
            weight=1,
            sector=self.sector
        )
        self.dishwashing = Function.objects.create(
            function="Dish Washing",
            weight=1,
            sector=self.sector
        )

        # Create skills
        self.washing_dishes = Skill.objects.create(
            skill="Washing dishes",
            category="hard"
        )
        self.customer_service = Skill.objects.create(
            skill="Customer service",
            category="soft"
        )
        self.cocktail_making = Skill.objects.create(
            skill="Cocktail making",
            category="hard"
        )

    def test_skill_weights_per_function(self):
        """Test that the same skill can have different weights for different functions"""
        # Add washing dishes skill to both functions with different weights
        FunctionSkill.objects.create(
            function=self.dishwashing,
            skill=self.washing_dishes,
            weight=10  # High weight for dish washing
        )
        FunctionSkill.objects.create(
            function=self.bartending,
            skill=self.washing_dishes,
            weight=2   # Low weight for bartending
        )

        # Verify weights
        dishwashing_skill = FunctionSkill.objects.get(
            function=self.dishwashing,
            skill=self.washing_dishes
        )
        bartending_skill = FunctionSkill.objects.get(
            function=self.bartending,
            skill=self.washing_dishes
        )

        self.assertEqual(dishwashing_skill.weight, 10)
        self.assertEqual(bartending_skill.weight, 2)

    def test_function_skills_ordering(self):
        """Test that skills are ordered by weight within a function"""
        # Add skills to bartending with different weights
        FunctionSkill.objects.create(
            function=self.bartending,
            skill=self.cocktail_making,
            weight=10  # Most important
        )
        FunctionSkill.objects.create(
            function=self.bartending,
            skill=self.customer_service,
            weight=8   # Second most important
        )
        FunctionSkill.objects.create(
            function=self.bartending,
            skill=self.washing_dishes,
            weight=2   # Least important
        )

        # Get ordered skills
        skills = FunctionSkill.objects.filter(function=self.bartending).order_by('-weight')
        ordered_skills = [fs.skill.skill for fs in skills]

        # Verify order
        self.assertEqual(ordered_skills, [
            "Cocktail making",
            "Customer service",
            "Washing dishes"
        ])

    def test_skill_functions_relationship(self):
        """Test the relationship between skills and functions"""
        # Add skills to functions
        FunctionSkill.objects.create(
            function=self.bartending,
            skill=self.washing_dishes,
            weight=2
        )
        FunctionSkill.objects.create(
            function=self.dishwashing,
            skill=self.washing_dishes,
            weight=10
        )

        # Check that the skill is associated with both functions
        skill_functions = self.washing_dishes.functions.all()
        self.assertEqual(skill_functions.count(), 2)
        self.assertIn(self.bartending, skill_functions)
        self.assertIn(self.dishwashing, skill_functions)

    def test_function_skills_through_model(self):
        """Test accessing skill weights through the function"""
        # Add skills with weights
        FunctionSkill.objects.create(
            function=self.bartending,
            skill=self.cocktail_making,
            weight=10
        )
        FunctionSkill.objects.create(
            function=self.bartending,
            skill=self.washing_dishes,
            weight=2
        )

        # Get skills with their weights
        function_skills = FunctionSkill.objects.filter(function=self.bartending)
        
        # Verify weights for each skill
        skill_weights = {fs.skill.skill: fs.weight for fs in function_skills}
        self.assertEqual(skill_weights["Cocktail making"], 10)
        self.assertEqual(skill_weights["Washing dishes"], 2)