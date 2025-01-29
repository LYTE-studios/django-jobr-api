from django.test import TestCase
from django.core.exceptions import ValidationError
from vacancies.models import (ContractType, Function, Question, Language, Skill)
from common.models import Extra

class CommonModelsTestCase(TestCase):
    def setUp(self):
        # Create sample data for testing
        self.contract_type = ContractType.objects.create(contract_type="Full-time")
        self.function = Function.objects.create(function="Software Developer")
        self.question = Question.objects.create(question="Tell me about your experience")
        self.language = Language.objects.create(language="English")
        self.skill_hard = Skill.objects.create(skill="Python", category="hard")
        self.skill_soft = Skill.objects.create(skill="Communication", category="soft")
        self.extra = Extra.objects.create(extra="Additional Information")

    def test_contract_type_creation(self):
        self.assertEqual(str(self.contract_type), "Full-time")
        self.assertEqual(self.contract_type.contract_type, "Full-time")

    def test_function_creation(self):
        self.assertEqual(str(self.function), "Software Developer")
        self.assertEqual(self.function.function, "Software Developer")

    def test_question_creation(self):
        self.assertEqual(str(self.question), "Tell me about your experience")
        self.assertEqual(self.question.question, "Tell me about your experience")

    def test_language_creation(self):
        self.assertEqual(str(self.language), "English")
        self.assertEqual(self.language.language, "English")

    def test_skill_creation(self):
        # Test hard skill
        self.assertEqual(str(self.skill_hard), "Python")
        self.assertEqual(self.skill_hard.skill, "Python")
        self.assertEqual(self.skill_hard.category, "hard")

        # Test soft skill
        self.assertEqual(str(self.skill_soft), "Communication")
        self.assertEqual(self.skill_soft.skill, "Communication")
        self.assertEqual(self.skill_soft.category, "soft")

    def test_skill_category_validation(self):
        # Test valid categories
        valid_hard_skill = Skill.objects.create(skill="Java", category="hard")
        valid_soft_skill = Skill.objects.create(skill="Teamwork", category="soft")
        
        # Test invalid category using full_clean()
        invalid_skill = Skill(skill="Invalid Skill", category="invalid")
        with self.assertRaises(ValidationError):
            invalid_skill.full_clean()

    def test_extra_creation(self):
        self.assertEqual(str(self.extra), "Additional Information")
        self.assertEqual(self.extra.extra, "Additional Information")

    def test_string_representation(self):
        # Ensure __str__ method works for all models
        models = [
            self.contract_type, 
            self.function, 
            self.question, 
            self.language, 
            self.skill_hard, 
            self.extra
        ]
        
        for model in models:
            self.assertTrue(isinstance(str(model), str))
            self.assertGreater(len(str(model)), 0)

    def test_field_max_lengths(self):
        # Test that fields accept valid length strings
        long_str = "x" * 255  # Maximum allowed length
        
        # Test ContractType
        contract = ContractType.objects.create(contract_type=long_str)
        self.assertEqual(len(contract.contract_type), 255)
        
        # Test Function
        function = Function.objects.create(function=long_str)
        self.assertEqual(len(function.function), 255)
        
        # Test Question
        question = Question.objects.create(question=long_str)
        self.assertEqual(len(question.question), 255)
        
        # Test Language
        language = Language.objects.create(language=long_str)
        self.assertEqual(len(language.language), 255)
        
        # Test Skill
        skill = Skill.objects.create(skill=long_str, category="hard")
        self.assertEqual(len(skill.skill), 255)
        
        # Test Extra
        extra = Extra.objects.create(extra=long_str)
        self.assertEqual(len(extra.extra), 255)