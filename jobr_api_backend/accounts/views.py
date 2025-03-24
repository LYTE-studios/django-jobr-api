from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import CustomUser, Employee, Employer, LikedEmployee
from .serializers import (
    UserSerializer,
    UserAuthenticationSerializer,
    LoginSerializer,
    ProfileImageUploadSerializer,
    EmployeeSearchSerializer,
    EmployerSearchSerializer,
    LikedEmployeeSerializer,
    VATValidationSerializer
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
                    "error": e.detail.get('error', 'VALIDATION_ERROR'),
                    "message": e.detail.get('message', str(e))
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
                    "error": "SERVICE_UNAVAILABLE",
                    "message": str(e)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class UserViewSet(viewsets.ModelViewSet):
    """Handle user operations."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset based on user role."""
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

    def perform_update(self, serializer):
        """Handle password updates."""
        user = serializer.save()
        if 'password' in self.request.data:
            user.set_password(self.request.data['password'])
            user.save()

class EmployeeSearchView(generics.ListAPIView):
    """Search for employees."""
    serializer_class = EmployeeSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter employees based on search criteria."""
        queryset = CustomUser.objects.filter(role='employee')
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(employee_profile__city_name__icontains=city)
        return queryset

class EmployerSearchView(generics.ListAPIView):
    """Search for employers."""
    serializer_class = EmployerSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter employers based on search criteria."""
        queryset = CustomUser.objects.filter(role='employer')
        company = self.request.query_params.get('company', None)
        if company:
            queryset = queryset.filter(employer_profile__company_name__icontains=company)
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