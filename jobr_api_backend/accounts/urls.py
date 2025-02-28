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
    AllEmployeeGalleriesView,
    EmployeeByUserView,
    UpdateEmployeeGalleryView,
    DeleteEmployeeGallery,
    AllEmployerGalleriesView,
    EmployerByUserView,
    UpdateEmployerGalleryView,
    DeleteEmployerGallery,
    EmployeeStatisticsView,
    ConnectionTestView,
    AISuggestionsView,
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
    path(
        "gallery/employee",
        AllEmployeeGalleriesView.as_view(),
        name="all-employee-galleries",
    ),
    path(
        "gallery/employee/<int:pk>",
        EmployeeByUserView.as_view(),
        name="employee-galleries-by-user",
    ),
    path(
        "gallery/employee/update",
        UpdateEmployeeGalleryView.as_view(),
        name="update-employee-galleries",
    ),
    path(
        "gallery/employee/delete",
        DeleteEmployeeGallery.as_view(),
        name="delete-employee-galleries",
    ),
    path(
        "gallery/employer",
        AllEmployerGalleriesView.as_view(),
        name="all-employer-galleries",
    ),
    path(
        "gallery/employer/<int:pk>",
        EmployerByUserView.as_view(),
        name="employer-galleries-by-user",
    ),
    path(
        "gallery/employer/update",
        UpdateEmployerGalleryView.as_view(),
        name="update-employer-galleries",
    ),
    path(
        "gallery/employer/delete",
        DeleteEmployerGallery.as_view(),
        name="delete-employer-galleries",
    ),
    path("login/google", GoogleSignInView.as_view(), name="google_signin"),
    path("login/apple", AppleSignInView.as_view(), name="apple_signin"),
    path("reviews", ReviewCreateView.as_view(), name="review-create"),
    path("statistics", EmployeeStatisticsView.as_view(), name="employee-statistics"),
    path("ai/suggestions/", AISuggestionsView.as_view(), name="ai-suggestions"),
]
