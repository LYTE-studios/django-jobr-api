from django.urls import path
from .views import matchmaking

urlpatterns = [
    path('matchmaking/<str:entity_type>/<int:entity_id>', matchmaking, name='matchmaking'),
]