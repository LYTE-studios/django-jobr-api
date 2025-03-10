from django.shortcuts import render
from django.db.models import Q
from accounts.models import Employee
from vacancies.models import Vacancy
from django.http import JsonResponse


# Create your views here.
def get_relevant_vacancies(employee):

    """
    Retrieves relevant vacancies for a given employee based on matching contract type,
    function, languages, and skills.

    This function filters the `Vacancy` model to return vacancies that match the 
    employee's contract type, function, and languages. It also filters vacancies based on
    the skills that the employee possesses. The results are distinct to avoid duplicates.

    Args:
        employee (Employee): An instance of the Employee model, representing the employee 
                              whose relevant vacancies are to be retrieved.

    Returns:
        QuerySet: A queryset of `Vacancy` objects that are relevant to the given employee.
    """
    return Vacancy.objects.filter(
        Q(contract_type=employee.contract_type)
        & Q(function=employee.function)
        & Q(language__in=employee.language.all())
        & Q(skill__in=employee.skill.all())
    ).distinct()


def get_relevant_employees(vacancy):

    """
    Retrieves relevant employees for a given vacancy based on matching contract type,
    function, languages, and skills.

    This function filters the `Employee` model to return employees who match the 
    vacancy's contract type, function, and languages. It also filters employees based on
    the skills required by the vacancy. The results are distinct to avoid duplicates.

    Args:
        vacancy (Vacancy): An instance of the Vacancy model, representing the vacancy 
                           for which relevant employees are to be retrieved.

    Returns:
        QuerySet: A queryset of `Employee` objects that are relevant to the given vacancy.
    """
    return Employee.objects.filter(
        Q(contract_type=vacancy.contract_type)
        & Q(function=vacancy.function)
        & Q(language__in=vacancy.language.all())
        & Q(skill__in=vacancy.skill.all())
    ).distinct()


def generate_matchmaking_prompt(entity_type, data, preferences):
    if entity_type == "employee":
        prompt = f"""
        You are an assistant helping employees find their best match among job vacancies. 
        The employee has the following profile: 
        - Skills: {', '.join(data['skills'])}
        - Contract Type: {data['contract_type']}
        - Function: {data['function']}
        - Preferred Languages: {', '.join(data['languages'])}
        - Desired Location: {data['location']}
        - Salary Expectation: {data['salary']}
        
        Here are the job vacancies:
        {preferences}

        Based on this information, rate them between 1~100 and find the top 3 matches and explain why they are a good fit.
        """
    elif entity_type == "employer":
        prompt = f"""
        You are an assistant helping employers find the best employees for their vacancies.
        The employer is looking for candidates with the following requirements:
        - Skills: {', '.join(data['skills'])}
        - Contract Type: {data['contract_type']}
        - Function: {data['function']}
        - Preferred Languages: {', '.join(data['languages'])}
        - Week Day Availability: {data['week_day']}
        
        Here are the employees:
        {preferences}

        Based on this information, rate them between 1~100 and find the top 3 matches and explain why they are a good fit.
        """
    return prompt


def matchmaking(request, entity_type, entity_id):
    if entity_type == "employee":
        employee = Employee.objects.get(id=entity_id)
        vacancies = get_relevant_vacancies(employee)
        serialized_vacancies = [
            {
                "title": v.title,
                "salary": v.salary,
                "skills": [s.name for s in v.skill.all()],
                "languages": [l.name for l in v.language.all()],
            }
            for v in vacancies
        ]
        prompt = generate_matchmaking_prompt(
            "employee",
            {
                "skills": [s.name for s in employee.skill.all()],
                "contract_type": (
                    employee.contract_type.name if employee.contract_type else "None"
                ),
                "function": employee.function.name if employee.function else "None",
                "languages": [l.name for l in employee.language.all()],
                "location": f"{employee.latitude}, {employee.longitude}",
                "salary": "Not specified",
            },
            serialized_vacancies,
        )
    elif entity_type == "employer":
        vacancy = Vacancy.objects.get(id=entity_id)
        employees = get_relevant_employees(vacancy)
        serialized_employees = [
            {
                "name": e.user.username,
                "skills": [s.name for s in e.skill.all()],
                "languages": [l.name for l in e.language.all()],
            }
            for e in employees
        ]
        prompt = generate_matchmaking_prompt(
            "employer",
            {
                "skills": [s.name for s in vacancy.skill.all()],
                "contract_type": (
                    vacancy.contract_type.name if vacancy.contract_type else "None"
                ),
                "function": vacancy.function.name if vacancy.function else "None",
                "languages": [l.name for l in vacancy.language.all()],
                "week_day": vacancy.week_day,
            },
            serialized_employees,
        )
    else:
        return JsonResponse({"error": "Invalid entity type"}, status=400)

    chatgpt_response = get_chatgpt_response(prompt)
    return JsonResponse({"response": chatgpt_response})
