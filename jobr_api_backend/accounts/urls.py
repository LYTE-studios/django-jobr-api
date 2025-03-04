# accounts/urls.py
from django.urls import path, include
from .views import (
    UserLoginView,
    UserRegistrationView,
    UserDetailView,
    EmployeeRegistration,
    EmployerRegistration,
    GoogleSignInView,
    AppleSignInView,
    ReviewCreateView,
    EmployeeStatisticsView,
    ConnectionTestView,
    AISuggestionsView,
    MyProfileView, UpdateUserGalleryView, DeleteUserGallery, DeleteAccountView,
)

urlpatterns = [
    path("login", UserLoginView.as_view(), name="login"),
    path("test-connection", ConnectionTestView.as_view(), name="test-connection"),
    path("register", UserRegistrationView.as_view(), name="register"),
    path(
        "users/<int:pk>", UserDetailView.as_view(), name="user-detail"
    ),  # Added user detail URL
    path(
        "register/employee",
        EmployeeRegistration.as_view(),
        name="employee-registration",
    ),
    path(
        "register/employer",
        EmployerRegistration.as_view(),
        name="employer-registration",
    ),
    path("login/google", GoogleSignInView.as_view(), name="google_signin"),
    path("login/apple", AppleSignInView.as_view(), name="apple_signin"),
    path("reviews", ReviewCreateView.as_view(), name="review-create"),
    path("statistics", EmployeeStatisticsView.as_view(), name="employee-statistics"),
    path("ai/suggestions/", AISuggestionsView.as_view(), name="ai-suggestions"),
    path("profile/", MyProfileView.as_view(), name="my-profile"),
    path(
        "gallery/user/update",
        UpdateUserGalleryView.as_view(),
        name="update-user-galleries",
    ),
    path(
        "gallery/user/delete",
        DeleteUserGallery.as_view(),
        name="delete-user-galleries",
    ),
    path('account/delete/', DeleteAccountView.as_view(), name='delete-account'),
]
