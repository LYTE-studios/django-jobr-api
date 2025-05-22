from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AppleNotificationView,
    UserViewSet,
    VATValidationView,
    EmployeeSearchView,
    EmployerSearchView,
    LikedEmployeeView,
    ReviewViewSet,
    LoginView,
    RegisterView,
    TestConnectionView,
    AISuggestionsView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    EmployeeFilterView,
    GoogleLoginView,
    AppleLoginView
)

# Create router
router = DefaultRouter()
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Profile endpoints
    path('profile/', UserViewSet.as_view({
        'get': 'profile',
        'put': 'profile',
        'patch': 'profile'
    }), name='profile-profile'),
    
    path('profile/select-company/', UserViewSet.as_view({
        'post': 'set_selected_company'
    }), name='profile-select-company'),
    
    path('profile/company/create/', UserViewSet.as_view({
        'post': 'create_company'
    }), name='profile-create-company'),
    
    path('profile/company/add/', UserViewSet.as_view({
        'post': 'add_company'
    }), name='profile-add-company'),
    
    # Image upload endpoints
    path('profile/picture/', UserViewSet.as_view({
        'post': 'update_profile_picture',
        'delete': 'delete_profile_picture'
    }), name='profile-picture'),
    
    path('profile/banner/', UserViewSet.as_view({
        'post': 'update_profile_banner',
        'delete': 'delete_profile_banner'
    }), name='profile-banner'),
    
    # Gallery endpoints
    path('profile/gallery/', UserViewSet.as_view({
        'post': 'add_gallery_image'
    }), name='profile-gallery-add'),
    path('profile/gallery/<int:pk>/', UserViewSet.as_view({
        'delete': 'delete_gallery_image'
    }), name='profile-gallery-delete'),

    # Authentication endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('login/google/', GoogleLoginView.as_view(), name='google-login'),
    path('login/apple/', AppleLoginView.as_view(), name='apple-login'),
    path('login/apple/notifications/', AppleNotificationView.as_view(), name='apple-notifications'),
    path('register/', RegisterView.as_view(), name='register'),
    path('test-connection/', TestConnectionView.as_view(), name='test-connection'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Profile endpoints
    path('users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('users/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='user-detail'),
    
    # Validation endpoints
    path('vat-validate/', VATValidationView.as_view(), name='validate-vat'),

    # Search and filter endpoints
    path('employees/search/', EmployeeSearchView.as_view(), name='employee-search'),
    path('employees/filter/', EmployeeFilterView.as_view(), name='employee-filter'),
    path('employers/search/', EmployerSearchView.as_view(), name='employer-search'),

    # Employee interaction endpoints
    path('employees/liked/', LikedEmployeeView.as_view(), name='liked-employees-list'),
    path('employees/<int:employee_id>/like/', LikedEmployeeView.as_view(), name='like-employee'),
    path('employees/ai/suggestions/', AISuggestionsView.as_view(), name='ai-suggestions'),

    # Review endpoints
    path('users/<int:user_id>/reviews/given/', ReviewViewSet.as_view({'get': 'list'}), {'type': 'given'}, name='user-reviews-given'),
    path('users/<int:user_id>/reviews/received/', ReviewViewSet.as_view({'get': 'list'}), {'type': 'received'}, name='user-reviews-received'),
]
