# vacancies/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VacancyViewSet,
    VacancyFilterView,
    LocationViewSet,
    ContractTypeViewSet,
    FunctionViewSet,
    LanguageViewSet,
    QuestionViewSet,
    SkillViewSet,
    FunctionSkillViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'locations', LocationViewSet, basename='locations')
router.register(r'contracts', ContractTypeViewSet, basename='contracts')
router.register(r'functions', FunctionViewSet, basename='functions')
router.register(r'languages', LanguageViewSet, basename='languages')
router.register(r'questions', QuestionViewSet, basename='questions')
router.register(r'skills', SkillViewSet, basename='skills')
router.register(r'function-skills', FunctionSkillViewSet, basename='function-skills')
router.register(r'', VacancyViewSet, basename='vacancy')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional endpoints
    path('filter/', VacancyFilterView.as_view(), name='vacancy-filter'),
]
