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
    SalaryBenefitViewSet,
    SectorViewSet,
    JobApplicationViewSet,
    FavoriteVacancyViewSet,
    AIVacancySuggestionsView,
    JobListingPromptViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'contracts', ContractTypeViewSet, basename='contract')
router.register(r'functions', FunctionViewSet, basename='function')
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'sectors', SectorViewSet, basename='sector')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'function-skills', FunctionSkillViewSet, basename='function-skill')
router.register(r'vacancies', VacancyViewSet, basename='vacancy')
router.register(r'salary-benefits', SalaryBenefitViewSet, basename='salary-benefit')
router.register(r'applications', JobApplicationViewSet, basename='application')
router.register(r'favorites', FavoriteVacancyViewSet, basename='favorite')
router.register(r'job-listing-prompts', JobListingPromptViewSet, basename='job-listing-prompt')

urlpatterns = [
    # Include router URLs
    path('', include((router.urls, 'vacancies'), namespace='vacancies')),
    
    # Additional endpoints
    path('filter/', VacancyFilterView.as_view(), name='vacancy-filter'),
    path('suggestions/', AIVacancySuggestionsView.as_view(), name='vacancy-suggestions'),
]
