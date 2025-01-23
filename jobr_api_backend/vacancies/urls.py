# vacancies/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VacancyViewSet, ApplyViewSet, VacancyFilterView, ContractsTypesView, FunctionsView, LanguagesView, SkillsView, LocationsView

router = DefaultRouter()
router.register(r'vacancies', VacancyViewSet, basename='vacancy')
router.register(r'apply', ApplyViewSet, basename='apply')
urlpatterns = [
    path('', include(router.urls)),
    path('locations', LocationsView.as_view(), name='locations',),
    path('skills', SkillsView.as_view(), name='skills'),
    path('languages', LanguagesView.as_view(), name='languages'),
    path('functions', FunctionsView.as_view(), name='functions'),
    path('contracts', ContractsTypesView.as_view(), name='contracts'),
    path('filter', VacancyFilterView.as_view(), name='vacancy-filter'),
]

