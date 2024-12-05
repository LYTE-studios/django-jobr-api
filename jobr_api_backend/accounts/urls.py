# accounts/urls.py
from django.urls import path
from .views import UserLoginView, UserDetailView, EmployeeRegistration, EmployerRegistration, GoogleSignInView, AppleSignInView, ReviewCreateView, EmployeeStatisticsView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),  # Added user detail URL
    path('register/employee/', EmployeeRegistration.as_view(), name='employee-registration'),
    path('register/employer/', EmployerRegistration.as_view(), name='employer-registration'),
    path('login/google/', GoogleSignInView.as_view(), name='google_signin'),
    path('login/apple/', AppleSignInView.as_view(), name='apple_signin'),
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),
    path('statistics/', EmployeeStatisticsView.as_view(), name='employee-statistics'),
]
