from django.test import TestCase
from vacancies.models import (
    Location,
    ContractType,
    Function,
    Question,
    Language,
    Skill,
    Weekday,
    SalaryBenefit,
    ProfileInterest,
    JobListingPrompt,
    MasteryOption
)

class LocationModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for Location model tests
        """
        self.location_data = {
            'location': 'Brussels',
            'weight': 10
        }
        self.location = Location.objects.create(**self.location_data)

    def test_location_creation(self):
        """
        Test creating a Location instance
        """
        self.assertEqual(self.location.location, self.location_data['location'])
        self.assertEqual(self.location.weight, self.location_data['weight'])

    def test_location_string_representation(self):
        """
        Test the string representation of a Location
        """
        expected_str = f"{self.location_data['location']} at {self.location_data['weight']}"
        self.assertEqual(str(self.location), expected_str)

    def test_location_null_weight(self):
        """
        Test Location with null weight
        """
        location = Location.objects.create(location='Antwerp')
        self.assertIsNone(location.weight)
        self.assertEqual(str(location), 'Antwerp at None')

class ContractTypeModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for ContractType model tests
        """
        self.contract_data = {
            'contract_type': 'Full-time',
            'weight': 5
        }
        self.contract = ContractType.objects.create(**self.contract_data)

    def test_contract_type_creation(self):
        """
        Test creating a ContractType instance
        """
        self.assertEqual(self.contract.contract_type, self.contract_data['contract_type'])
        self.assertEqual(self.contract.weight, self.contract_data['weight'])

    def test_contract_type_string_representation(self):
        """
        Test the string representation of a ContractType
        """
        expected_str = f"{self.contract_data['contract_type']} at {self.contract_data['weight']}"
        self.assertEqual(str(self.contract), expected_str)

class FunctionModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for Function model tests
        """
        self.function_data = {
            'function': 'Software Developer',
            'weight': 8
        }
        self.function = Function.objects.create(**self.function_data)

    def test_function_creation(self):
        """
        Test creating a Function instance
        """
        self.assertEqual(self.function.function, self.function_data['function'])
        self.assertEqual(self.function.weight, self.function_data['weight'])

    def test_function_string_representation(self):
        """
        Test the string representation of a Function
        """
        expected_str = f"{self.function_data['function']} at {self.function_data['weight']}"
        self.assertEqual(str(self.function), expected_str)

class SkillModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for Skill model tests
        """
        self.skill_data = {
            'skill': 'Python',
            'category': 'hard',
            'weight': 7
        }
        self.skill = Skill.objects.create(**self.skill_data)

    def test_skill_creation(self):
        """
        Test creating a Skill instance
        """
        self.assertEqual(self.skill.skill, self.skill_data['skill'])
        self.assertEqual(self.skill.category, self.skill_data['category'])
        self.assertEqual(self.skill.weight, self.skill_data['weight'])

    def test_skill_string_representation(self):
        """
        Test the string representation of a Skill
        """
        expected_str = f"{self.skill_data['skill']} - {self.skill_data['category']} at {self.skill_data['weight']}"
        self.assertEqual(str(self.skill), expected_str)

    def test_skill_category_choices(self):
        """
        Test Skill category choices
        """
        # Test valid categories
        skill1 = Skill.objects.create(skill='Java', category='hard')
        skill2 = Skill.objects.create(skill='Leadership', category='soft')
        
        self.assertEqual(skill1.category, 'hard')
        self.assertEqual(skill2.category, 'soft')
        
        # Test default category
        skill3 = Skill.objects.create(skill='Python')
        self.assertEqual(skill3.category, 'hard')

class WeekdayModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for Weekday model tests
        """
        self.weekday_data = {
            'name': 'Monday'
        }
        self.weekday = Weekday.objects.create(**self.weekday_data)

    def test_weekday_creation(self):
        """
        Test creating a Weekday instance
        """
        self.assertEqual(self.weekday.name, self.weekday_data['name'])

    def test_weekday_string_representation(self):
        """
        Test the string representation of a Weekday
        """
        self.assertEqual(str(self.weekday), self.weekday_data['name'])

    def test_weekday_unique_constraint(self):
        """
        Test that Weekday names must be unique
        """
        with self.assertRaises(Exception):
            Weekday.objects.create(name='Monday')

class MasteryOptionTests(TestCase):
    def test_mastery_option_choices(self):
        """
        Test MasteryOption choices
        """
        self.assertEqual(MasteryOption.NONE, "None")
        self.assertEqual(MasteryOption.BEGINNER, "Beginner")
        self.assertEqual(MasteryOption.INTERMEDIATE, "Intermediate")
        self.assertEqual(MasteryOption.ADVANCED, "Advanced")
        self.assertEqual(MasteryOption.EXPERT, "Expert")

    def test_mastery_option_choices_list(self):
        """
        Test that all mastery options are available in choices
        """
        choices = [choice[0] for choice in MasteryOption.choices]
        self.assertIn("None", choices)
        self.assertIn("Beginner", choices)
        self.assertIn("Intermediate", choices)
        self.assertIn("Advanced", choices)
        self.assertIn("Expert", choices)