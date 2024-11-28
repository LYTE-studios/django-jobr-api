# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractTypeViewSet, FunctionViewSet, QuestionViewSet, SkillViewSet, VacancyViewSet, LanguageViewSet, ApplyViewSet

router = DefaultRouter()
router.register(r'contract-types', ContractTypeViewSet, basename='contract_type')
router.register(r'functions', FunctionViewSet, basename='function')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'extras', SkillViewSet, basename='extra')
router.register(r'vacancies', VacancyViewSet, basename='vacancy')
router.register(r'apply', ApplyViewSet, basename='apply')
urlpatterns = [
    path('', include(router.urls)),
]
