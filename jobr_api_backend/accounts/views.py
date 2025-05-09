from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Company, CompanyUser, CustomUser, Employee, LikedEmployee,
    ProfileOption, Review, CompanyGallery, EmployeeGallery
)
from .serializers import (
    CompanySerializer,
    UserSerializer,
    UserAuthenticationSerializer,
    LoginSerializer,
    CompanyImageUploadSerializer,
    EmployeeImageUploadSerializer,
    EmployeeSearchSerializer,
    EmployerSearchSerializer,
    LikedEmployeeSerializer,
    VATValidationSerializer,
    ReviewSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    GoogleAuthSerializer,
    AppleAuthSerializer
)
from .services import VATValidationService
from django.core.cache import cache
from rest_framework.exceptions import ValidationError, Throttled, PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt
from django.conf import settings

class GoogleLoginView(generics.GenericAPIView):
    """Handle Google Sign-In."""
    permission_classes = [AllowAny]
    serializer_class = GoogleAuthSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Verify the Google ID token
            idinfo = id_token.verify_oauth2_token(
                serializer.validated_data['id_token'],
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            # Get or create user
            try:
                user = CustomUser.objects.get(email=idinfo['email'])
                # Update user's role if not set
                if not user.role:
                    user.role = serializer.validated_data['role']
                    user.save()
            except CustomUser.DoesNotExist:
                # Create new user
                user = CustomUser.objects.create_user(
                    username=idinfo['email'],
                    email=idinfo['email'],
                    first_name=idinfo.get('given_name', ''),
                    last_name=idinfo.get('family_name', ''),
                    role=serializer.validated_data['role']
                )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })

        except ValueError:
            return Response(
                {'error': 'Invalid Google ID token'},
                status=status.HTTP_400_BAD_REQUEST
            )

class AppleLoginView(generics.GenericAPIView):
    """Handle Apple Sign-In."""
    permission_classes = [AllowAny]
    serializer_class = AppleAuthSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Verify the Apple ID token
            decoded_token = jwt.decode(
                serializer.validated_data['id_token'],
                settings.APPLE_PUBLIC_KEY,
                algorithms=['RS256'],
                audience=settings.APPLE_BUNDLE_ID
            )

            # Get the email from the token
            email = decoded_token.get('email')
            if not email:
                return Response(
                    {'error': 'Email not found in Apple ID token'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get or create user
            try:
                user = CustomUser.objects.get(email=email)
                # Update user's role if not set
                if not user.role:
                    user.role = serializer.validated_data['role']
                    user.save()
            except CustomUser.DoesNotExist:
                # Create new user
                user = CustomUser.objects.create_user(
                    username=email,
                    email=email,
                    role=serializer.validated_data['role']
                )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })

        except jwt.InvalidTokenError:
            return Response(
                {'error': 'Invalid Apple ID token'},
                status=status.HTTP_400_BAD_REQUEST
            )

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

class PasswordResetRequestView(generics.GenericAPIView):
    """
    Request a password reset email.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = CustomUser.objects.get(email=email)

        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Send password reset email
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
        send_mail(
            'Password Reset Request',
            f'Click the following link to reset your password: {reset_url}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response(
            {"detail": "Password reset email has been sent."},
            status=status.HTTP_200_OK
        )

class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Confirm password reset and set new password.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response(
                {"detail": "Invalid reset link."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired reset link."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK
        )

class VATValidationView(generics.GenericAPIView):
    """Validate VAT numbers and retrieve company details."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        vat_number = request.GET.get('vat_number')
        if not vat_number:
            return Response(
                {
                    "error": "MISSING_PARAMETER",
                    "message": "vat_number parameter is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Remove spaces and '+' characters from the VAT number
        vat_number = vat_number.replace(' ', '').replace('+', '')
        try:
            # Get client IP for rate limiting
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            # Get selected company if available
            company = None
            if request.user.role == ProfileOption.EMPLOYER:
                company = request.user.selected_company

            # Check cache first
            cache_key = f"vat_validation_{vat_number}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return Response(cached_result)

            # Validate VAT number
            result = VATValidationService.validate_vat(vat_number, ip, company)

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

    @action(detail=False, methods=['delete'])
    def delete_profile_picture(self, request):
        """Delete profile picture based on user role."""
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

        if target.profile_picture:
            target.profile_picture.delete()
            target.profile_picture = None
            target.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'])
    def delete_profile_banner(self, request):
        """Delete profile banner based on user role."""
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

        if target.profile_banner:
            target.profile_banner.delete()
            target.profile_banner = None
            target.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='gallery')
    def add_gallery_image(self, request):
        """Add an image to company's or employee's gallery."""
        if 'image' not in request.FILES:
            return Response(
                {"error": "No image provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.role == ProfileOption.EMPLOYER:
            if not request.user.selected_company:
                return Response(
                    {"error": "No company selected"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            gallery = CompanyGallery.objects.create(
                company=request.user.selected_company,
                gallery=request.FILES['image']
            )
            
            from .serializers import CompanySerializer
            return Response(CompanySerializer(request.user.selected_company).data)
        
        elif request.user.role == ProfileOption.EMPLOYEE:
            if not hasattr(request.user, 'employee_profile'):
                return Response(
                    {"error": "Employee profile not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            gallery = EmployeeGallery.objects.create(
                employee=request.user.employee_profile,
                gallery=request.FILES['image']
            )
            
            from .serializers import UserSerializer
            return Response(UserSerializer(request.user).data)
        
        return Response(
            {"error": "Invalid user role for gallery upload"},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=True, methods=['delete'], url_path='gallery')
    def delete_gallery_image(self, request, pk=None):
        """Delete an image from company's or employee's gallery."""
        if request.user.role == ProfileOption.EMPLOYER:
            if not request.user.selected_company:
                return Response(
                    {"error": "No company selected"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            gallery = get_object_or_404(
                CompanyGallery,
                pk=pk,
                company=request.user.selected_company
            )
            
        elif request.user.role == ProfileOption.EMPLOYEE:
            if not hasattr(request.user, 'employee_profile'):
                return Response(
                    {"error": "Employee profile not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            gallery = get_object_or_404(
                EmployeeGallery,
                pk=pk,
                employee=request.user.employee_profile
            )
            
        else:
            return Response(
                {"error": "Invalid user role for gallery deletion"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Delete the file first
        if gallery.gallery:
            gallery.gallery.delete()
        # Then delete the model instance
        gallery.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def create_company(self, request):
        """Create a new company and add it to the user's companies."""
        if request.user.role != ProfileOption.EMPLOYER:
            return Response(
                {"error": "Only employer users can create companies"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Use CompanySerializer to validate and create the company
        serializer = CompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()

        # Handle profile picture URL if present
        profile_picture_url = request.data.get('profile_picture_url')
        if profile_picture_url:
            # Extract relative path from full URL
            relative_path = profile_picture_url.split('/media/')[-1]
            company.profile_picture = relative_path
        
        # Handle profile banner URL if present
        profile_banner_url = request.data.get('profile_banner_url')
        if profile_banner_url:
            relative_path = profile_banner_url.split('/media/')[-1]
            company.profile_banner = relative_path
        
        # Save company with images
        company.save()

        # Handle gallery images if present
        gallery_data = request.data.get('company_gallery', [])
        for gallery_item in gallery_data:
            if gallery_url := gallery_item.get('gallery_url'):
                relative_path = gallery_url.split('/media/')[-1]
                CompanyGallery.objects.create(
                    company=company,
                    gallery=relative_path
                )

        # Create CompanyUser relationship with 'owner' role
        CompanyUser.objects.create(
            company=company,
            user=request.user,
            role='owner'
        )

        # Always set the newly created company as the selected company
        request.user.selected_company = company
        request.user.save()

        # Return updated company data with image URLs
        updated_serializer = CompanySerializer(company)
        return Response(updated_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def add_company(self, request):
        """Add an existing company to the user's companies."""
        if request.user.role != ProfileOption.EMPLOYER:
            return Response(
                {"error": "Only employer users can add companies"},
                status=status.HTTP_403_FORBIDDEN
            )

        company_id = request.data.get('company_id')
        role = request.data.get('role', 'member')  # Default role is member

        if not company_id:
            return Response(
                {"error": "company_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate role
        valid_roles = ['owner', 'admin', 'member']
        if role not in valid_roles:
            return Response(
                {"error": f"Invalid role. Must be one of: {', '.join(valid_roles)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if relationship already exists
        if CompanyUser.objects.filter(company=company, user=request.user).exists():
            return Response(
                {"error": "User is already associated with this company"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create CompanyUser relationship
        company_user = CompanyUser.objects.create(
            company=company,
            user=request.user,
            role=role
        )

        # Set as selected company if user doesn't have one
        if not request.user.selected_company:
            request.user.selected_company = company
            request.user.save()

        return Response(CompanySerializer(company).data)

    @action(detail=False, methods=['post'])
    def set_selected_company(self, request):
        """Set the selected company for an employer user."""
        if request.user.role != ProfileOption.EMPLOYER:
            return Response(
                {"error": "Only employer users can select a company"},
                status=status.HTTP_403_FORBIDDEN
            )

        company_id = request.data.get('company_id')
        if not company_id:
            return Response(
                {"error": "company_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            company = Company.objects.get(
                id=company_id,
                users=request.user
            )
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found or you don't have access to it"},
                status=status.HTTP_404_NOT_FOUND
            )

        request.user.selected_company = company
        request.user.save()

        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

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
            
            # Let the serializer handle all profile updates
            pass

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
    """Search for companies."""
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Filter companies based on search term and having visible vacancies."""
        queryset = Company.objects.filter(vacancies__isnull=False).distinct()
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(city__icontains=search) |
                Q(website__icontains=search) |
                Q(vat_number__icontains=search) |
                Q(sector__name__icontains=search)
            ).distinct()
        return queryset


class LikedEmployeeView(generics.GenericAPIView):
    """Handle liked employee operations."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get liked employees for the current employer's company."""
        if request.user.role != ProfileOption.EMPLOYER or not request.user.selected_company:
            return Response([])
        
        # Get the users of liked employees
        liked_employee_users = CustomUser.objects.filter(
            employee_profile__liked_by_companies__company=request.user.selected_company
        )
        return Response(UserSerializer(liked_employee_users, many=True).data)

    def post(self, request, *args, **kwargs):
        """Toggle like status for an employee."""
        if not self.request.user.selected_company:
            raise ValidationError("No company selected")
        
        # Get user_id from URL kwargs
        user_id = self.kwargs.get('employee_id')  # keeping the URL param name for backwards compatibility
        if not user_id:
            raise ValidationError("User ID is required")
            
        # Get the employee instance through the CustomUser
        user = get_object_or_404(CustomUser, id=user_id, role=ProfileOption.EMPLOYEE)
        employee = user.employee_profile
        
        # Check if the like already exists
        existing_like = LikedEmployee.objects.filter(
            company=self.request.user.selected_company,
            employee=employee
        ).first()
        
        if existing_like:
            # Unlike if already liked
            existing_like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        # Like if not already liked
        LikedEmployee.objects.create(
            company=request.user.selected_company,
            liked_by=request.user,
            employee=employee
        )
        
        # Return the updated user data
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        """Remove a liked employee relationship."""
        if not request.user.selected_company:
            raise ValidationError("No company selected")
        # Get the employee through CustomUser
        user = get_object_or_404(CustomUser, id=pk, role=ProfileOption.EMPLOYEE)
        liked = get_object_or_404(
            LikedEmployee,
            company=request.user.selected_company,
            employee=user.employee_profile
        )
        liked.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EmployeeFilterView(generics.ListAPIView):
    """Filter employees based on various criteria."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Filter employees based on query parameters."""
        queryset = CustomUser.objects.filter(role=ProfileOption.EMPLOYEE)
        
        # Filter by distance to company
        max_distance = self.request.query_params.get('max_distance')
        if max_distance and self.request.user.role == ProfileOption.EMPLOYER and self.request.user.selected_company:
            # Skip distance filtering if coordinates aren't available
            pass

        # Filter by age range
        min_age = self.request.query_params.get('min_age')
        max_age = self.request.query_params.get('max_age')
        if min_age or max_age:
            from datetime import date, timedelta
            today = date.today()
            if min_age:
                max_date = today - timedelta(days=int(min_age) * 365)
                queryset = queryset.filter(employee_profile__date_of_birth__lte=max_date)
            if max_age:
                min_date = today - timedelta(days=int(max_age) * 365)
                queryset = queryset.filter(employee_profile__date_of_birth__gte=min_date)

        # Filter by gender
        gender = self.request.query_params.get('gender')
        if gender:
            queryset = queryset.filter(employee_profile__gender=gender)

        # Filter by languages
        languages = self.request.query_params.getlist('languages')
        if languages:
            queryset = queryset.filter(employee_profile__language__id__in=languages)

        # Filter by skills
        skills = self.request.query_params.getlist('skills')
        if skills:
            queryset = queryset.filter(employee_profile__skill__id__in=skills)

        # Filter by contract type
        contract_type = self.request.query_params.get('contract_type')
        if contract_type:
            queryset = queryset.filter(employee_profile__contract_type_id=contract_type)

        return queryset.distinct()

class AISuggestionsView(generics.ListAPIView):
    """Get AI-powered employee suggestions."""
    serializer_class = UserSerializer
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