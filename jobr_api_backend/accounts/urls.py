# accounts/urls.py
from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserDetailView, EmployeeRegistration, EmployerRegistration, AdminRegistration

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),  # Added user detail URL
    path('register/employee/', EmployeeRegistration.as_view(), name='employee-registration'),
    path('register/employer/', EmployerRegistration.as_view(), name='employer-registration'),
]
