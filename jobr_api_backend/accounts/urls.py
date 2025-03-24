from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserLoginView,
    MyProfileView,
    ProfileImageUploadView,
    ConnectionTestView,
    GoogleSignInView,
    AppleSignInView,
    UserDetailView,
    LikeEmployeeView,
    LikedEmployeesListView,
    EmployeeSearchView,
    VATValidationView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('google-signin/', GoogleSignInView.as_view(), name='google-signin'),
    path('apple-signin/', AppleSignInView.as_view(), name='apple-signin'),
    
    # Profile endpoints
    path('profile/', MyProfileView.as_view(), name='my-profile'),
    path('profile/image/', ProfileImageUploadView.as_view(), name='profile-image-upload'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    
    # Utility endpoints
    path('test-connection/', ConnectionTestView.as_view(), name='test-connection'),
    path('validate-vat/', VATValidationView.as_view(), name='validate-vat'),

    # Employee interaction endpoints
    path('employees/search/', EmployeeSearchView.as_view(), name='employee-search'),
    path('employees/liked/', LikedEmployeesListView.as_view(), name='liked-employees-list'),
    path('employees/<int:employee_id>/like/', LikeEmployeeView.as_view(), name='like-employee'),
]
