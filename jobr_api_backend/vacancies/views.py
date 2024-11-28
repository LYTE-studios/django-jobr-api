from rest_framework import viewsets
from .models import ContractType, Function, Question, Skill, Extra, Vacancy, Language, ApplyVacancy
from .serializers import ContractTypeSerializer, LanguageSerializer, QuestionSerializer, SkillSerializer, \
    ExtraSerializer, VacancySerializer, ApplySerializer, FunctionSerializer


class ContractTypeViewSet(viewsets.ModelViewSet):
    queryset = ContractType.objects.all()
    serializer_class = ContractTypeSerializer


class FunctionViewSet(viewsets.ModelViewSet):
    queryset = Function.objects.all()
    serializer_class = FunctionSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class ExtraViewSet(viewsets.ModelViewSet):
    queryset = Extra.objects.all()
    serializer_class = ExtraSerializer


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer


class ApplyViewSet(viewsets.ModelViewSet):
    queryset = ApplyVacancy.objects.all()
    serializer_class = ApplySerializer

