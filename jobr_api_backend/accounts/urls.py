# accounts/urls.py
from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserDetailView, EmployeeRegistration, EmployerRegistration, AdminRegistration

urlpatterns = [
    # path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),  # Added user detail URL
    path('register/employee/', EmployeeRegistration.as_view(), name='employee-registration'),
    path('register/employer/', EmployerRegistration.as_view(), name='employer-registration'),
    path('register/admin/', AdminRegistration.as_view(), name='admin-registration'),
]
