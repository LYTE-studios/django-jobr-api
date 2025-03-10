from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import ContractType, Function, Language, Skill, Location, Question
from accounts.models import Employer
from .models import Vacancy, ApplyVacancy
from .serializers import (
    VacancySerializer,
    ApplySerializer,
    ContractTypeSerializer,
    FunctionSerializer,
    LanguageSerializer,
    SkillSerializer,
    LocationSerializer,
    QuestionSerializer,
)
from math import radians, cos, sin, asin, sqrt
from rest_framework import generics
from rest_framework import status
from accounts.models import Employee
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from chat.models import ChatRoom
from chat.serializers import ChatRoomSerializer


class LocationsView(generics.GenericAPIView):
    """
    This view handles the retrieval of all Location objects.

    Authentication:
        JWT authentication is required to access this view.
    
    Methods:
        get: Retrieves all Location objects from the database and returns them serialized in the response.
    """
    authentication_classes = [JWTAuthentication]
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve all Location objects.

        Arguments:
            request: The HTTP request object.
        
        Returns:
            Response: A serialized list of all Location objects.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SkillsView(generics.GenericAPIView):
    """
    This view handles the retrieval of all Skill objects.

    Authentication:
        JWT authentication is required to access this view.
    
    Methods:
        get: Retrieves all Skill objects from the database and returns them serialized in the response.
    """
    authentication_classes = [JWTAuthentication]
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve all Skill objects.

        Arguments:
            request: The HTTP request object.
        
        Returns:
            Response: A serialized list of all Skill objects.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LanguagesView(generics.GenericAPIView):
    """
    This view handles the retrieval of all Language objects.

    Authentication:
        JWT authentication is required to access this view.
    
    Methods:
        get: Retrieves all Language objects from the database and returns them serialized in the response.
    """
    authentication_classes = [JWTAuthentication]
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve all Language objects.

        Arguments:
            request: The HTTP request object.
        
        Returns:
            Response: A serialized list of all Language objects.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FunctionsView(generics.GenericAPIView):
    """
    API view to retrieve a list of Function instances.
    
    This view allows authenticated users to retrieve a list of all available 
    functions from the Function model. It returns data serialized into JSON format.

    Authentication:
        JWT authentication is required to access this view.

     Methods:
        get:
            Handles GET requests to retrieve a list of Function instances.
            Returns a list of serialized Function objects as JSON data.
    """
    authentication_classes = [JWTAuthentication]
    queryset = Function.objects.all()
    serializer_class = FunctionSerializer

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve a list of Function instances.
        
        This method retrieves all Function objects from the database,
        serializes them using the FunctionSerializer, and returns the 
        serialized data in JSON format.

        Returns:
            Response: A response containing a list of serialized Function objects.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class QuestionsView(generics.GenericAPIView):
    """
    API view to retrieve a list of Question instances.
    
    This view allows authenticated users to retrieve a list of all available 
    questions from the Question model. It returns data serialized into JSON format.

    Authentication:
       JWT authentication is required to access this view.

    Methods:
        get:
            Handles GET requests to retrieve a list of Question instances.
            Returns a list of serialized Question objects as JSON data.
    """
    authentication_classes = [JWTAuthentication]
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve a list of Question instances.
        
        This method retrieves all Question objects from the database,
        serializes them using the QuestionSerializer, and returns the 
        serialized data in JSON format.

        Returns:
            Response: A response containing a list of serialized Question objects.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ContractsTypesView(generics.GenericAPIView):
    """
    API view to retrieve a list of ContractType instances.
    
    This view allows authenticated users to retrieve a list of all available 
    contract types from the ContractType model. It returns data serialized into JSON format.

    Authentication:
        JWT authentication is required to access this view.

    Methods:
        get:
            Handles GET requests to retrieve a list of ContractType instances.
            Returns a list of serialized ContractType objects as JSON data.
    """
    authentication_classes = [JWTAuthentication]
    queryset = ContractType.objects.all()
    serializer_class = ContractTypeSerializer

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve a list of ContractType instances.
        
        This method retrieves all ContractType objects from the database,
        serializes them using the ContractTypeSerializer, and returns the 
        serialized data in JSON format.

        Returns:
            Response: A response containing a list of serialized ContractType objects.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class VacancyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Vacancy objects.
    
    Authentication:
        JWT authentication is required to access this view.
    
    Methods:
        - create: Creates a new vacancy and assigns the current user as the employer.
    """
    authentication_classes = [JWTAuthentication]

    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

    def create(self, request, *args, **kwargs):
        """
        Creates a new Vacancy instance.
        
        This method automatically adds the current user's ID as the employer when creating a vacancy.
        
        Args:
            request: The HTTP request containing vacancy data.

        Returns:
            Response: A response with the serialized vacancy data or errors.
        """
        data = request.data.copy()
        data["employer"] = request.user.id
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ApplyVacancy objects.
    
    Authentication:
        JWT authentication is required to access this view.
    """
    authentication_classes = [JWTAuthentication]

    queryset = ApplyVacancy.objects.all()
    serializer_class = ApplySerializer


class VacancyFilterView(generics.ListAPIView):
    """
    API view for filtering and retrieving job vacancies based on various criteria.
    
    This view allows users to filter job vacancies using multiple parameters such as:
    - Contract type
    - Function
    - Required skills
    - Distance from an employee's location
    - Sorting by salary (ascending or descending)
    
    Authentication:
        - JWT authentication is required to access this view.

    Query Parameters:
        - contract_type (int): ID of the contract type to filter vacancies.
        - function (int): ID of the function (job role) to filter vacancies.
        - skills (list of int): List of skill IDs to filter vacancies.
        - employee_id (int): ID of the employee to filter vacancies by proximity.
        - distance (float): Maximum distance (in km) from the employee's location.
        - sort_by_salary (str): Sort vacancies by salary ('asc' for ascending, 'desc' for descending).

    Methods:
        - get_queryset(): Retrieves and filters vacancies based on query parameters.
        - calculate_distance(lat1, lon1, lat2, lon2): Computes the great-circle distance (Haversine formula) between two geographic points.

    Returns:
        - A list of vacancies matching the given criteria.
    """
    authentication_classes = [JWTAuthentication]

    serializer_class = VacancySerializer

    def get_queryset(self):
        """
        Retrieves and filters the vacancy queryset based on query parameters.

        Filtering logic:
            - Filters vacancies by contract type if provided.
            - Filters vacancies by function if provided.
            - Filters vacancies by required skills if provided.
            - If an employee ID is provided, retrieves their latitude and longitude.
            - If a maximum distance is provided, filters vacancies within that radius.
            - Sorts vacancies by salary if sorting is requested.

        Returns:
            QuerySet: A filtered list of Vacancy objects.
        """
        queryset = Vacancy.objects.all()

        # Get parameters from request
        contract_type = self.request.query_params.get("contract_type")
        function = self.request.query_params.get("function")
        skills = self.request.query_params.getlist("skills")
        employee_id = self.request.query_params.get("employee_id", None)
        max_distance = self.request.query_params.get("distance", None)
        sort_by_salary = self.request.query_params.get("sort_by_salary", None)
        # Retrieve employee's latitude and longitude
        user_latitude = None
        user_longitude = None

        if employee_id:
            try:
                employee = Employee.objects.get(id=employee_id)
                user_latitude = employee.latitude
                user_longitude = employee.longitude
            except Employee.DoesNotExist:
                raise NotFound("Employee not found.")

        # Filter by contract_type
        if contract_type:
            queryset = queryset.filter(contract_type__id=contract_type)

        # Filter by function
        if function:
            queryset = queryset.filter(function__id=function)

        # Filter by skills
        if skills:
            queryset = queryset.filter(skill__id__in=skills).distinct()
        # Filter by distance if latitude and longitude are available
        if max_distance and user_latitude is not None and user_longitude is not None:
            queryset = [
                vacancy
                for vacancy in queryset
                if self.calculate_distance(
                    user_latitude, user_longitude, vacancy.latitude, vacancy.longitude
                )
                <= float(max_distance)
            ]

        # Sort by salary
        if sort_by_salary:
            if sort_by_salary.lower() == "asc":
                queryset = queryset.order_by("salary")
            elif sort_by_salary.lower() == "desc":
                queryset = queryset.order_by("-salary")

        return queryset

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance between two points
        on the Earth using the Haversine formula.
        
        Parameters:
            - lat1 (float): Latitude of the first point.
            - lon1 (float): Longitude of the first point.
            - lat2 (float): Latitude of the second point.
            - lon2 (float): Longitude of the second point.

        Returns:
            float: Distance in kilometers between the two points.
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r


class ApplyForJobView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplySerializer

    def post(self, request, *args, **kwargs):
        vacancy_id = self.kwargs.get('vacancy_id')
        try:
            vacancy = Vacancy.objects.get(id=vacancy_id)
        except Vacancy.DoesNotExist:
            return Response({"detail": "Vacancy not found."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "employee": request.user.employee_profile.id,
            "vacancy": vacancy.id
        }
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            chatroom = ChatRoom.objects.create(
                employee=request.user.employee_profile,
                employer=vacancy.employer,
                vacancy=vacancy
            )
            chatroom_serializer = ChatRoomSerializer(chatroom)
            response_data = serializer.data
            response_data['chatroom'] = chatroom_serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)