from rest_framework import viewsets
from common.models import ContractType, Function, Question, Skill, Extra, Language
from .models import Vacancy, ApplyVacancy
from .serializers import ContractTypeSerializer, LanguageSerializer, QuestionSerializer, SkillSerializer, \
    ExtraSerializer, VacancySerializer, ApplySerializer, FunctionSerializer
from math import radians, cos, sin, asin, sqrt
from rest_framework import generics
from accounts.models import Employee
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.authentication import JWTAuthentication



class ContractTypeViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]

    queryset = ContractType.objects.all()
    serializer_class = ContractTypeSerializer


class FunctionViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]

    queryset = Function.objects.all()
    serializer_class = FunctionSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class SkillViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class ExtraViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]

    queryset = Extra.objects.all()
    serializer_class = ExtraSerializer


class VacancyViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]

    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer


class ApplyViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]

    queryset = ApplyVacancy.objects.all()
    serializer_class = ApplySerializer


class VacancyFilterView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]

    serializer_class = VacancySerializer

    def get_queryset(self):
        queryset = Vacancy.objects.all()

        # Get parameters from request
        contract_type = self.request.query_params.get('contract_type')
        function = self.request.query_params.get('function')
        skills = self.request.query_params.getlist('skills')
        employee_id = self.request.query_params.get('employee_id', None)
        max_distance = self.request.query_params.get('distance', None)

        # Retrieve employee's latitude and longitude
        user_latitude = None
        user_longitude = None

        if employee_id:
            try:
                employee = Employee.objects.get(id=employee_id)
                user_latitude = employee.latitude
                user_longitude = employee.longitude
            except Employee.DoesNotExist:
                raise NotFound('Employee not found.')

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
                vacancy for vacancy in queryset
                if self.calculate_distance(user_latitude, user_longitude, vacancy.latitude, vacancy.longitude) <= float(
                    max_distance)
            ]

        return queryset

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

