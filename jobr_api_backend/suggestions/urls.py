from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AISuggestionViewSet

router = DefaultRouter()
router.register(r'suggestions', AISuggestionViewSet, basename='suggestion')

urlpatterns = router.urls