from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserViewSet,
    VATValidationView,
    EmployeeSearchView,
    EmployerSearchView,
    LikedEmployeeView,
    ReviewViewSet,
    LoginView,
    RegisterView,
    TestConnectionView
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
    path('register/', RegisterView.as_view(), name='register'),
    path('test-connection/', TestConnectionView.as_view(), name='test-connection'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Profile endpoints
    path('users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('users/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='user-detail'),
    
    # Validation endpoints
    path('validate-vat/', VATValidationView.as_view(), name='validate-vat'),

    # Search endpoints
    path('employees/search/', EmployeeSearchView.as_view(), name='employee-search'),
    path('employers/search/', EmployerSearchView.as_view(), name='employer-search'),

    # Employee interaction endpoints
    path('employees/liked/', LikedEmployeeView.as_view(), name='liked-employees-list'),
    path('employees/<int:employee_id>/like/', LikedEmployeeView.as_view(), name='like-employee'),

    # Review endpoints
    path('users/<int:user_id>/reviews/given/', ReviewViewSet.as_view({'get': 'list'}), {'type': 'given'}, name='user-reviews-given'),
    path('users/<int:user_id>/reviews/received/', ReviewViewSet.as_view({'get': 'list'}), {'type': 'received'}, name='user-reviews-received'),
]
