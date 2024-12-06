from django.shortcuts import render, get_object_or_404
from .models import Match
from accounts.models import Employee, Employer
from vacancies.models import Vacancy, ContractType, Skill, Language 
from django.http import JsonResponse
from .utils import get_best_matching_vacancies, enhanced_match_score, apply_for_vacancy

def get_best_matches_for_employee(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    matches = Match.objects.filter(employee=employee).order_by('-match_score')  # Fetch matches sorted by score
    match_data = [
        {
            "employer": match.employer.company_name,
            "match_score": match.match_score
        }
        for match in matches
    ]
    return JsonResponse(match_data, safe=False)

def get_best_matches_for_employer(request, employer_id):
    employer = Employer.objects.get(id=employer_id)
    matches = Match.objects.filter(employer=employer).order_by('-match_score')
    match_data = [
        {
            "employee": match.employee.user.username,
            "match_score": match.match_score
        }
        for match in matches
    ]
    return JsonResponse(match_data, safe=False)

def get_best_matches(request, employee_id):
    """Get best matches for an employee based on vacancies and reviews."""
    employee = get_object_or_404(Employee, id=employee_id)
    best_matches = []

    # Fetch best matches based on vacancies and reputation
    for vacancy, vacancy_score in get_best_matching_vacancies(employee):
        employer = vacancy.employer
        match_score = enhanced_match_score(employee, employer)

        best_matches.append({
            "employer": employer.company_name,
            "match_score": match_score,
            "vacancy_score": vacancy_score,
            "reputation_score": employer.reputation_score,
            "vacancy_title": vacancy.title,
            "vacancy_location": vacancy.location,
            "vacancy_salary": vacancy.salary
        })

    return JsonResponse({"best_matches": best_matches})


def apply_for_job(request, employee_id, vacancy_id):
    """Allow an employee to apply for a specific vacancy."""
    employee = get_object_or_404(Employee, id=employee_id)
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    result = apply_for_vacancy(employee, vacancy)
    return JsonResponse({"result": result})
