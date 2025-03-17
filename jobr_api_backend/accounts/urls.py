from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    MyProfileView,
    ProfileImageUploadView,
    ConnectionTestView,
    GoogleSignInView,
    AppleSignInView,
    UserDetailView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/', MyProfileView.as_view(), name='my-profile'),
    path('profile/image/', ProfileImageUploadView.as_view(), name='profile-image-upload'),
    path('test-connection/', ConnectionTestView.as_view(), name='test-connection'),
    path('google-signin/', GoogleSignInView.as_view(), name='google-signin'),
    path('apple-signin/', AppleSignInView.as_view(), name='apple-signin'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
