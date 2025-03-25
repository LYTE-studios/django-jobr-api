from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import (
    CustomUser, Employee, Employer, LikedEmployee,
    ProfileOption, Review, UserGallery
)
from .serializers import (
    UserSerializer,
    UserAuthenticationSerializer,
    LoginSerializer,
    ProfileImageUploadSerializer,
    EmployeeSearchSerializer,
    EmployerSearchSerializer,
    LikedEmployeeSerializer,
    VATValidationSerializer,
    ReviewSerializer
)
from .services import VATValidationService
from django.core.cache import cache
from rest_framework.exceptions import ValidationError, Throttled

class VATValidationView(generics.GenericAPIView):
    """Validate VAT numbers and retrieve company details."""
    permission_classes = [IsAuthenticated]
    serializer_class = VATValidationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vat_number = serializer.validated_data['vat_number']

        try:
            # Get client IP for rate limiting
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            # Get employer if available
            employer = None
            if hasattr(request.user, 'employer_profile'):
                employer = request.user.employer_profile

            # Check cache first
            cache_key = f"vat_validation_{vat_number}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return Response(cached_result)

            # Validate VAT number
            result = VATValidationService.validate_vat(vat_number, ip, employer)

            # Cache the result
            cache.set(cache_key, result, timeout=86400)  # 24 hours

            return Response(result)

        except ValidationError as e:
            return Response(
                {
                    "error": "INVALID_FORMAT",
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Throttled as e:
            return Response(
                {
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": str(e)
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        except Exception as e:
            return Response(
                {
                    "error": "INVALID_FORMAT",
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class UserViewSet(viewsets.ModelViewSet):
    """Handle user operations."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset based on action and role."""
        if self.action == 'profile':
            # For profile endpoint, return only the current user
            return CustomUser.objects.filter(id=self.request.user.id)
        
        # For other endpoints, filter by role if specified
        queryset = CustomUser.objects.all()
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def perform_create(self, serializer):
        """Set password when creating a new user."""
        user = serializer.save()
        if 'password' in self.request.data:
            user.set_password(self.request.data['password'])
            user.save()

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='profile', url_name='profile')
    def profile(self, request):
        """Get or update current user's profile."""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        
        # PUT or PATCH
        serializer = self.get_serializer(request.user, data=request.data, partial=request.method == 'PATCH')
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def update_profile(self, request):
        """Update current user's profile."""
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='profile-picture')
    def update_profile_picture(self, request):
        """Update user's profile picture."""
        serializer = ProfileImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if user.profile_picture:
            user.profile_picture.delete()
        user.profile_picture = serializer.validated_data['image']
        user.save()
        
        return Response(UserSerializer(user).data)

    @action(detail=False, methods=['delete'], url_path='profile-picture')
    def delete_profile_picture(self, request):
        """Delete user's profile picture."""
        user = request.user
        if user.profile_picture:
            user.profile_picture.delete()
            user.profile_picture = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='profile-banner')
    def update_profile_banner(self, request):
        """Update user's profile banner."""
        serializer = ProfileImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if user.profile_banner:
            user.profile_banner.delete()
        user.profile_banner = serializer.validated_data['image']
        user.save()
        
        return Response(UserSerializer(user).data)

    @action(detail=False, methods=['delete'], url_path='profile-banner')
    def delete_profile_banner(self, request):
        """Delete user's profile banner."""
        user = request.user
        if user.profile_banner:
            user.profile_banner.delete()
            user.profile_banner = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='gallery')
    def add_gallery_image(self, request):
        """Add an image to user's gallery."""
        serializer = ProfileImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        gallery = UserGallery.objects.create(
            user=request.user,
            gallery=serializer.validated_data['image']
        )
        
        return Response(UserSerializer(request.user).data)

    @action(detail=True, methods=['delete'], url_path='gallery')
    def delete_gallery_image(self, request, pk=None):
        """Delete an image from user's gallery."""
        gallery = get_object_or_404(UserGallery, pk=pk, user=request.user)
        gallery.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        """Handle password updates and profile data."""
        user = serializer.save()
        
        # Handle password updates
        if 'password' in self.request.data:
            user.set_password(self.request.data['password'])
            user.save()

        # Handle employee profile updates
        if 'employee_profile' in self.request.data and user.role == 'employee':
            profile_data = self.request.data['employee_profile']
            if not user.employee_profile:
                user.employee_profile = Employee.objects.create(user=user)
            for key, value in profile_data.items():
                setattr(user.employee_profile, key, value)
            user.employee_profile.save()

        # Handle employer profile updates
        if 'employer_profile' in self.request.data and user.role == 'employer':
            profile_data = self.request.data['employer_profile']
            if not user.employer_profile:
                user.employer_profile = Employer.objects.create(user=user)
            for key, value in profile_data.items():
                setattr(user.employer_profile, key, value)
            user.employer_profile.save()

class EmployeeSearchView(generics.ListAPIView):
    """Search for employees."""
    serializer_class = EmployeeSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter employees based on search criteria."""
        queryset = CustomUser.objects.filter(role=ProfileOption.EMPLOYEE)
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(employee_profile__city_name__icontains=city)
        return queryset.distinct()

class EmployerSearchView(generics.ListAPIView):
    """Search for employers."""
    serializer_class = EmployerSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter employers based on search criteria."""
        queryset = CustomUser.objects.filter(role=ProfileOption.EMPLOYER)
        company = self.request.query_params.get('company', None)
        if company:
            queryset = queryset.filter(employer_profile__company_name__icontains=company)
        return queryset.distinct()

class LikedEmployeeView(generics.ListCreateAPIView):
    """Handle liked employee operations."""
    serializer_class = LikedEmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get liked employees for the current employer."""
        if not hasattr(self.request.user, 'employer_profile'):
            return LikedEmployee.objects.none()
        return LikedEmployee.objects.filter(employer=self.request.user.employer_profile)

    def perform_create(self, serializer):
        """Create a new liked employee relationship."""
        serializer.save(employer=self.request.user.employer_profile)

    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        """Remove a liked employee relationship."""
        liked = get_object_or_404(
            LikedEmployee,
            employer=request.user.employer_profile,
            employee_id=pk
        )
        liked.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewViewSet(viewsets.ModelViewSet):
    """Handle review operations."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter reviews based on user and query parameters."""
        queryset = Review.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        review_type = self.request.query_params.get('type', None)  # 'given' or 'received'

        if user_id:
            if review_type == 'given':
                queryset = queryset.filter(reviewer_id=user_id)
            elif review_type == 'received':
                queryset = queryset.filter(reviewed_id=user_id)
            else:
                queryset = queryset.filter(reviewer_id=user_id) | queryset.filter(reviewed_id=user_id)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Set reviewer to current user when creating a review."""
        serializer.save(reviewer=self.request.user)

    def update(self, request, *args, **kwargs):
        """Only allow updating own reviews."""
        instance = self.get_object()
        if instance.reviewer != request.user:
            return Response(
                {"detail": "You can only update your own reviews."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Only allow deleting own reviews."""
        instance = self.get_object()
        if instance.reviewer != request.user:
            return Response(
                {"detail": "You can only delete your own reviews."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)