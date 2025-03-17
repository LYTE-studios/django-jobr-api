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
    authentication_classes = [JWTAuthentication]
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SkillsView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LanguagesView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FunctionsView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = Function.objects.all()
    serializer_class = FunctionSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class QuestionsView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ContractsTypesView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = ContractType.objects.all()
    serializer_class = ContractTypeSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class VacancyViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = VacancySerializer

    def get_queryset(self):
        # This ensures that only vacancies created by the logged-in user are returned
        queryset = Vacancy.objects.select_related('employer', 'location', 'function')
        if self.request.method == 'GET' and 'pk' not in self.kwargs:
            return queryset.filter(employer=self.request.user).distinct()
        return queryset.filter(employer=self.request.user).distinct()

class ApplyViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]

    queryset = ApplyVacancy.objects.all()
    serializer_class = ApplySerializer


class VacancyFilterView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = VacancySerializer

    def get_queryset(self):
        queryset = Vacancy.objects.all().distinct()

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
            max_distance = float(max_distance)
            # Using raw SQL for distance calculation
            queryset = queryset.extra(
                select={'distance': '''
                    6371 * 2 * ASIN(
                        SQRT(
                            POW(SIN(RADIANS(%s - ABS(latitude)) / 2), 2) +
                            COS(RADIANS(%s)) * COS(RADIANS(ABS(latitude))) *
                            POW(SIN(RADIANS(%s - longitude) / 2), 2)
                        )
                    )
                '''},
                select_params=[user_latitude, user_latitude, user_longitude],
                where=['latitude IS NOT NULL', 'longitude IS NOT NULL']
            ).filter(distance__lte=max_distance)

        # Sort by salary
        if sort_by_salary:
            if sort_by_salary.lower() == "asc":
                queryset = queryset.order_by("salary")
            elif sort_by_salary.lower() == "desc":
                queryset = queryset.order_by("-salary")

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance between two points
        on the Earth using the Haversine formula.
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