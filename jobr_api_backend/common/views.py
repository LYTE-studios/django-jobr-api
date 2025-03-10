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

    """
     Generates a matchmaking prompt for either an employee or an employer based on provided data.

    This function generates a detailed prompt that can be used by an assistant (such as an AI) 
    to rate job vacancies for an employee or rate potential employees for an employer. The prompt 
    includes the relevant profile information for the entity (either employee or employer) and 
    requests a ranking of preferences based on matching criteria.

    Args:
        entity_type (str): The type of the entity. Can be either "employee" or "employer". 
                           It determines whether the matchmaking is for an employee looking for 
                           a job or an employer looking for employees.
        data (dict): A dictionary containing the profile data for the entity. 
        preferences (str): A string representing the list of job vacancies or employee profiles 
                           that will be compared against the `data`. This could be a formatted 
                           list or detailed descriptions, depending on the context.

    Returns:
        str: A formatted prompt string that provides the assistant with all necessary information 
             to perform matchmaking and rank options (job vacancies or employees).
    """

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

    """
    Handles the matchmaking process for either employees or employers by generating a prompt 
    for an assistant to rate job matches for employees or employee matches for employers.

    This function retrieves the relevant data for either an employee or employer based on the 
    `entity_type` and `entity_id`, creates a prompt that includes the necessary details, 
    and sends the prompt to a chatbot (such as ChatGPT) to get a response. The matchmaking 
    process is based on the attributes of skills, languages, contract type, function, and 
    location for employees, and similar criteria for employers.

    Args:
        request (HttpRequest): The HTTP request object that triggered the matchmaking process.
        entity_type (str): The type of the entity, either "employee" or "employer". 
                           This determines whether the matchmaking process is for an employee 
                           looking for job vacancies or an employer looking for candidates.
        entity_id (int): The ID of the entity (either an employee or an employer) to retrieve 
                         from the database for matchmaking.

    Returns:
        JsonResponse: A JSON response containing the assistant's matchmaking response. 
                      The response contains a `response` field with the chatbot's output.
                      In case of an invalid entity type, returns a 400 error response with an 
                      error message.
    """
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
