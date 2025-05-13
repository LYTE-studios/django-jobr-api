from typing import List, Dict, Any
from django.db.models import Q
from django.conf import settings
from accounts.models import Employee
from vacancies.models import Vacancy
from .models import AISuggestion, SuggestionWeight
import openai


class SuggestionService:
    """Service for generating AI-powered suggestions."""

    @staticmethod
    def calculate_distance_score(employee_coords: tuple, vacancy_coords: tuple) -> float:
        """Calculate score based on distance between employee and vacancy."""
        from math import radians, sin, cos, sqrt, atan2

        lat1, lon1 = map(radians, employee_coords)
        lat2, lon2 = map(radians, vacancy_coords)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = 6371 * c  # Earth's radius in km

        # Convert distance to score (0-100)
        # Assuming max reasonable distance is 100km
        return max(0, 100 - (distance / 100) * 100)

    @staticmethod
    def calculate_language_score(employee_languages: List[Dict], vacancy_languages: List[Dict]) -> float:
        """Calculate score based on language matches."""
        if not vacancy_languages:
            return 100  # If vacancy doesn't require languages, perfect score

        total_score = 0
        for v_lang in vacancy_languages:
            best_match = 0
            for e_lang in employee_languages:
                if e_lang['language'] == v_lang['language']:
                    mastery_values = {
                        'beginner': 25,
                        'intermediate': 50,
                        'advanced': 75,
                        'native': 100
                    }
                    employee_mastery = mastery_values[e_lang['mastery']]
                    required_mastery = mastery_values[v_lang['mastery']]
                    match_score = min(100, (employee_mastery / required_mastery) * 100)
                    best_match = max(best_match, match_score)
            total_score += best_match

        return total_score / len(vacancy_languages)

    @staticmethod
    def calculate_skills_score(employee_skills: List[str], vacancy_skills: List[str]) -> float:
        """Calculate score based on skill matches."""
        if not vacancy_skills:
            return 100  # If vacancy doesn't require skills, perfect score

        matched_skills = set(employee_skills) & set(vacancy_skills)
        return (len(matched_skills) / len(vacancy_skills)) * 100

    @staticmethod
    def get_llm_score(employee_data: Dict[str, Any], vacancy_data: Dict[str, Any]) -> tuple:
        """Get qualitative score and explanation from LLM."""
        prompt = f"""
        You are an expert HR professional. Analyze the following employee and vacancy data and provide:
        1. A match score (0-100)
        2. A brief explanation of why this match would be good or not good.

        Employee:
        - Biography: {employee_data['biography']}
        - Interests: {', '.join(employee_data['interests'])}
        - Education: {employee_data['education']}

        Vacancy:
        - Description: {vacancy_data['description']}
        - Questions: {', '.join(vacancy_data['questions'])}
        - Company Description: {vacancy_data['company_description']}

        Respond in the following format:
        Score: [number]
        Explanation: [your explanation]
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert HR professional."},
                {"role": "user", "content": prompt}
            ]
        )

        text = response.choices[0].message.content
        score_line = next(line for line in text.split('\n') if line.startswith('Score:'))
        explanation_line = next(line for line in text.split('\n') if line.startswith('Explanation:'))

        score = float(score_line.split(':')[1].strip())
        explanation = explanation_line.split(':')[1].strip()

        return score, explanation

    @classmethod
    def generate_suggestions(cls) -> None:
        """Generate AI suggestions for all employees and vacancies."""
        # Get weights for current calculations
        weights = {w.name: w.weight for w in SuggestionWeight.objects.all()}
        default_weight = 20  # Default weight if not specified

        # Clear existing suggestions
        AISuggestion.objects.all().delete()

        # Get all active employees and vacancies
        employees = Employee.objects.filter(user__is_active=True)
        vacancies = Vacancy.objects.filter(is_active=True)

        for employee in employees:
            for vacancy in vacancies:
                # Calculate quantitative scores
                distance_score = cls.calculate_distance_score(
                    (employee.latitude, employee.longitude),
                    (vacancy.latitude, vacancy.longitude)
                )

                language_score = cls.calculate_language_score(
                    employee.language.all(),
                    vacancy.required_languages.all()
                )

                skills_score = cls.calculate_skills_score(
                    [s.name for s in employee.skills.all()],
                    [s.name for s in vacancy.required_skills.all()]
                )

                # Calculate weighted quantitative score
                quantitative_score = (
                    distance_score * weights.get('distance', default_weight) +
                    language_score * weights.get('language', default_weight) +
                    skills_score * weights.get('skills', default_weight)
                ) / (
                    weights.get('distance', default_weight) +
                    weights.get('language', default_weight) +
                    weights.get('skills', default_weight)
                )

                # Get qualitative score from LLM
                employee_data = {
                    'biography': employee.biography,
                    'interests': employee.interests,
                    'education': [e.name for e in employee.education.all()],
                }
                vacancy_data = {
                    'description': vacancy.description,
                    'questions': [q.text for q in vacancy.questions.all()],
                    'company_description': vacancy.company.description,
                }
                qualitative_score, explanation = cls.get_llm_score(employee_data, vacancy_data)

                # Calculate total score
                total_score = (
                    quantitative_score * weights.get('quantitative', 50) +
                    qualitative_score * weights.get('qualitative', 50)
                ) / (
                    weights.get('quantitative', 50) +
                    weights.get('qualitative', 50)
                )

                # Create suggestion
                AISuggestion.objects.create(
                    employee=employee,
                    vacancy=vacancy,
                    quantitative_score=quantitative_score,
                    qualitative_score=qualitative_score,
                    total_score=total_score,
                    message=explanation
                )