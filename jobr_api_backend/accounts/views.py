from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import (
    CustomUser, Employee, LikedEmployee,
    ProfileOption, Review, UserGallery
)
from .serializers import (
    UserSerializer,
    UserAuthenticationSerializer,
    LoginSerializer,
    CompanyImageUploadSerializer,
    EmployeeImageUploadSerializer,
    EmployeeSearchSerializer,
    EmployerSearchSerializer,
    LikedEmployeeSerializer,
    VATValidationSerializer,
    ReviewSerializer
)
from .services import VATValidationService
from django.core.cache import cache
from rest_framework.exceptions import ValidationError, Throttled
from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(generics.GenericAPIView):
    """Handle user login."""
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

class RegisterView(generics.CreateAPIView):
    """Handle user registration."""
    permission_classes = [AllowAny]
    serializer_class = UserAuthenticationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class TestConnectionView(generics.GenericAPIView):
    """Test if the user's token is valid."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        return Response({
            'message': 'Connection successful',
            'user': self.get_serializer(request.user).data
        })

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
        """Get or update current user's profile or company details."""
        if request.method == 'GET':
            if request.user.role == ProfileOption.EMPLOYER and request.user.selected_company:
                # Return company details for employers
                from .serializers import CompanySerializer
                serializer = CompanySerializer(request.user.selected_company)
                return Response(serializer.data)
            else:
                # Return user details for employees and employers without selected company
                serializer = self.get_serializer(request.user)
                return Response(serializer.data)
        
        # PUT or PATCH
        if request.user.role == ProfileOption.EMPLOYER and request.user.selected_company:
            # Update company details
            from .serializers import CompanySerializer
            serializer = CompanySerializer(
                request.user.selected_company,
                data=request.data,
                partial=request.method == 'PATCH'
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            # Update user details
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=request.method == 'PATCH'
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        
        return Response(serializer.data)
    @action(detail=False, methods=['post'])
    def update_profile_picture(self, request):
        """Update profile picture based on user role."""
        if request.user.role == ProfileOption.EMPLOYER:
            if not request.user.selected_company:
                return Response(
                    {"detail": "No company selected."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            target = request.user.selected_company
            serializer = CompanyImageUploadSerializer(data={'image_type': 'profile_picture', 'image': request.FILES.get('image')})
        elif request.user.role == ProfileOption.EMPLOYEE:
            if not hasattr(request.user, 'employee_profile'):
                return Response(
                    {"detail": "Employee profile not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            target = request.user.employee_profile
            serializer = EmployeeImageUploadSerializer(data={'image_type': 'profile_picture', 'image': request.FILES.get('image')})
        else:
            return Response(
                {"detail": "Invalid user role for image upload."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer.is_valid(raise_exception=True)
        if target.profile_picture:
            target.profile_picture.delete()
        target.profile_picture = serializer.validated_data['image']
        target.save()
        return Response({"detail": "Profile picture updated successfully"})

    @action(detail=False, methods=['post'])
    def update_profile_banner(self, request):
        """Update profile banner based on user role."""
        if request.user.role == ProfileOption.EMPLOYER:
            if not request.user.selected_company:
                return Response(
                    {"detail": "No company selected."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            target = request.user.selected_company
            serializer = CompanyImageUploadSerializer(data={'image_type': 'profile_banner', 'image': request.FILES.get('image')})
        elif request.user.role == ProfileOption.EMPLOYEE:
            if not hasattr(request.user, 'employee_profile'):
                return Response(
                    {"detail": "Employee profile not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            target = request.user.employee_profile
            serializer = EmployeeImageUploadSerializer(data={'image_type': 'profile_banner', 'image': request.FILES.get('image')})
        else:
            return Response(
                {"detail": "Invalid user role for image upload."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer.is_valid(raise_exception=True)
        if target.profile_banner:
            target.profile_banner.delete()
        target.profile_banner = serializer.validated_data['image']
        target.save()
        return Response({"detail": "Profile banner updated successfully"})

    @action(detail=False, methods=['delete'], url_path='profile-image/(?P<image_type>profile-picture|profile-banner)')
    def delete_profile_image(self, request, image_type):
        """Delete profile picture or banner based on user role."""
        if request.user.role == ProfileOption.EMPLOYER:
            if not request.user.selected_company:
                return Response(
                    {"detail": "No company selected."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            target = request.user.selected_company
        elif request.user.role == ProfileOption.EMPLOYEE:
            if not hasattr(request.user, 'employee_profile'):
                return Response(
                    {"detail": "Employee profile not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            target = request.user.employee_profile
        else:
            return Response(
                {"detail": "Invalid user role for image deletion."},
                status=status.HTTP_403_FORBIDDEN
            )

        if image_type == 'profile-picture':
            if target.profile_picture:
                target.profile_picture.delete()
                target.profile_picture = None
        else:  # profile-banner
            if target.profile_banner:
                target.profile_banner.delete()
                target.profile_banner = None

        target.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='gallery')
    def add_gallery_image(self, request):
        """Add an image to user's gallery."""
        if 'image' not in request.FILES:
            return Response(
                {"error": "No image provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        gallery = UserGallery.objects.create(
            user=request.user,
            gallery=request.FILES['image']
        )
        
        return Response(UserSerializer(request.user).data)

    @action(detail=True, methods=['delete'], url_path='gallery')
    def delete_gallery_image(self, request, pk=None):
        """Delete an image from user's gallery."""
        gallery = get_object_or_404(UserGallery, pk=pk, user=request.user)
        # Delete the file first
        if gallery.gallery:
            gallery.gallery.delete()
        # Then delete the model instance
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

class EmployeeSearchView(generics.ListAPIView):
    """Search for employees."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Filter employees based on search term."""
        queryset = CustomUser.objects.filter(role=ProfileOption.EMPLOYEE)
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(employee_profile__biography__icontains=search) |
                Q(employee_profile__city_name__icontains=search) |
                Q(employee_profile__function__name__icontains=search) |
                Q(employee_profile__skill__name__icontains=search) |
                Q(employee_profile__language__name__icontains=search)
            ).distinct()
        return queryset

class EmployerSearchView(generics.ListAPIView):
    """Search for employers."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Filter employers based on search term."""
        queryset = CustomUser.objects.filter(role=ProfileOption.EMPLOYER)
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(employer_profile__company_name__icontains=search) |
                Q(employer_profile__biography__icontains=search) |
                Q(employer_profile__city__icontains=search) |
                Q(employer_profile__website__icontains=search) |
                Q(employer_profile__vat_number__icontains=search)
            ).distinct()
        return queryset


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

class AISuggestionsView(generics.ListAPIView):
    """Get AI-powered employee suggestions."""
    serializer_class = EmployeeSearchSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Return top 5 employees (placeholder for AI implementation)."""
        return CustomUser.objects.filter(
            role=ProfileOption.EMPLOYEE,
            is_active=True
        ).order_by('-date_joined')[:5]

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