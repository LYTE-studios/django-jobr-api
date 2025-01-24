# vacancies/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VacancyViewSet, ApplyViewSet, VacancyFilterView, ContractsTypesView, FunctionsView, LanguagesView, SkillsView, LocationsView, QuestionsView

router = DefaultRouter()
router.register('apply', ApplyViewSet, basename='apply')
urlpatterns = [
    path('', include(router.urls)),
    path('locations', LocationsView.as_view(), name='locations',),
    path('skills', SkillsView.as_view(), name='skills'),
    path('languages', LanguagesView.as_view(), name='languages'),
    path('functions', FunctionsView.as_view(), name='functions'),
    path('contracts', ContractsTypesView.as_view(), name='contracts'),
    path('questions', QuestionsView.as_view(), name='questions'),
    path('filter', VacancyFilterView.as_view(), name='vacancy-filter'),
    path('vacancies', VacancyViewSet.as_view({'get': 'list', 'post': 'create'}), name='vacancies'),
]

