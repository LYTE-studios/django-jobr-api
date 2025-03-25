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
    FunctionSkillViewSet,
    SalaryBenefitViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'contracts', ContractTypeViewSet, basename='contract')
router.register(r'functions', FunctionViewSet, basename='function')
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'function-skills', FunctionSkillViewSet, basename='function-skill')
router.register(r'vacancies', VacancyViewSet, basename='vacancy')
router.register(r'salary-benefits', SalaryBenefitViewSet, basename='salary-benefit')

# The router will generate URLs like:
# /locations/ -> location-list
# /locations/{id}/ -> location-detail
# /functions/ -> function-list
# /functions/{id}/ -> function-detail
# /skills/ -> skill-list
# /skills/{id}/ -> skill-detail
# etc.

urlpatterns = [
    # Include router URLs
    path('', include((router.urls, 'vacancies'), namespace='vacancies')),
    
    # Additional endpoints
    path('filter/', VacancyFilterView.as_view(), name='vacancy-filter'),
]
