from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.forms import ValidationError
from django.http import Http404
from django.db.models import Prefetch

from rest_framework import generics, status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination

import google.auth.transport.requests
import google.oauth2.id_token
import firebase_admin
from firebase_admin import auth as firebase_auth

from .services import TokenService, VATValidationService
from .models import Employee, Employer, UserGallery, ProfileOption, LikedEmployee
from .serializers import (
    LoginSerializer,
    UserAuthenticationSerializer,
    ReviewSerializer,
    UserGallerySerializer,
    UserSerializer,
    ProfileImageUploadSerializer,
    LikedEmployeeSerializer,
    EmployeeSearchSerializer,
    VATValidationSerializer
)
from django.db.models import Q

User = get_user_model()

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ConnectionTestView(APIView):
    """
    A view to test the connection by returning the user's role.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "role": request.user.role,
        })

class UserRegistrationView(generics.CreateAPIView):
    """
    View for registering a new user and generating authentication tokens.
    """
    permission_classes = [AllowAny]
    serializer_class = UserAuthenticationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = TokenService.get_tokens_for_user(user)

        return Response({
            "access": tokens["access"], 
            "refresh": tokens["refresh"]
        }, status=status.HTTP_201_CREATED)

class UserLoginView(generics.GenericAPIView):
    """
    View for handling user login and generating authentication tokens.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = TokenService.get_tokens_for_user(user)

        return Response({
            "message": "Login successful",
            "user": user.username,
            "role": user.role,
            "access": tokens["access"],
            "refresh": tokens["refresh"]
        }, status=status.HTTP_200_OK)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for handling user details.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

class MyProfileView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating the current user's profile.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class GoogleSignInView(APIView):
    """
    Handles Google sign-in via Firebase authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            id_token = request.data.get("id_token")

            if not id_token:
                return Response(
                    {"error": "ID token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            request_google = google.auth.transport.requests.Request()
            try:
                id_info = google.oauth2.id_token.verify_firebase_token(
                    id_token, request_google, settings.GOOGLE_CLIENT_ID
                )
            except ValueError as e:
                return Response(
                    {"error": "Invalid token", "details": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            email = id_info.get("email")
            name = id_info.get("name", "")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "first_name": name.split()[0] if name else "",
                    "last_name": name.split()[-1] if len(name.split()) > 1 else "",
                },
            )

            return Response(
                {
                    "message": "Google Login successful",
                    "user": user.username,
                    "created": created,
                }
                | TokenService.get_tokens_for_user(user),
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": "Google Authentication failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AppleSignInView(APIView):
    """
    Handles Apple sign-in via Firebase authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            id_token = request.data.get("id_token")

            if not id_token:
                return Response(
                    {"error": "ID token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                decoded_token = firebase_auth.verify_id_token(id_token)
            except (ValueError, firebase_auth.InvalidIdTokenError) as e:
                return Response(
                    {"error": "Invalid token", "details": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            email = decoded_token.get("email")
            apple_uid = decoded_token.get("uid")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": f"apple_{apple_uid}",
                },
            )

            return Response(
                {
                    "message": "Apple Login successful",
                    "user": user.username,
                    "created": created,
                }
                | TokenService.get_tokens_for_user(user),
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": "Apple Authentication failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProfileImageUploadView(APIView):
    """
    View for uploading profile pictures and banners.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        serializer = ProfileImageUploadSerializer(
            instance=request.user, 
            data=request.data, 
            context={'request': request}
        )

        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response({
                    'message': f'{serializer.validated_data["image_type"].replace("_", " ").title()} uploaded successfully',
                    'image_url': user.profile_picture.url if serializer.validated_data['image_type'] == 'profile_picture' else user.profile_banner.url
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': f'Error uploading image: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        image_type = request.query_params.get('image_type')

        if image_type not in ['profile_picture', 'profile_banner']:
            return Response({
                'error': 'Invalid image type. Must be profile_picture or profile_banner.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        try:
            if image_type == 'profile_picture':
                if user.profile_picture:
                    user.profile_picture.delete()
                    user.profile_picture = None
            else:
                if user.profile_banner:
                    user.profile_banner.delete()
                    user.profile_banner = None
            
            user.save()
            return Response({
                'message': f'{image_type.replace("_", " ").title()} deleted successfully'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': f'Error deleting {image_type}: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class LikeEmployeeView(APIView):
    """
    View for liking/unliking employees and getting liked employees list.
    Only accessible by employers.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, employee_id):
        """Like an employee"""
        if request.user.role != ProfileOption.EMPLOYER:
            return Response(
                {"error": "Only employers can like employees"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            employee_user = User.objects.get(
                id=employee_id,
                role=ProfileOption.EMPLOYEE
            )
            employer = request.user.employer_profile

            # Create the like if it doesn't exist
            like, created = LikedEmployee.objects.get_or_create(
                employer=employer,
                employee=employee_user.employee_profile
            )

            if not created:
                return Response(
                    {"message": "Employee already liked"},
                    status=status.HTTP_200_OK
                )

            return Response(
                {"message": "Employee liked successfully"},
                status=status.HTTP_201_CREATED
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Employee not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, employee_id):
        """Unlike an employee"""
        if request.user.role != ProfileOption.EMPLOYER:
            return Response(
                {"error": "Only employers can unlike employees"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            employee_user = User.objects.get(
                id=employee_id,
                role=ProfileOption.EMPLOYEE
            )
            like = LikedEmployee.objects.get(
                employer=request.user.employer_profile,
                employee=employee_user.employee_profile
            )
            like.delete()
            return Response(
                {"message": "Employee unliked successfully"},
                status=status.HTTP_200_OK
            )
        except (User.DoesNotExist, LikedEmployee.DoesNotExist):
            return Response(
                {"error": "Like not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class LikedEmployeesListView(generics.ListAPIView):
    """
    View for getting the list of employees liked by the current employer.
    Only accessible by employers.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LikedEmployeeSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.role != ProfileOption.EMPLOYER:
            return LikedEmployee.objects.none()
        return LikedEmployee.objects.filter(
            employer=self.request.user.employer_profile
        ).select_related('employee__customuser')

class EmployeeSearchView(generics.ListAPIView):
    """
    View for searching employees based on various criteria.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeSearchSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = User.objects.filter(role=ProfileOption.EMPLOYEE).select_related('employee_profile')
        search_term = self.request.query_params.get('search', '')
        
        if search_term:
            queryset = queryset.filter(
                Q(username__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(employee_profile__city_name__icontains=search_term) |
                Q(employee_profile__biography__icontains=search_term)
            )

        # Additional filters
        city = self.request.query_params.get('city', '')
        if city:
            queryset = queryset.filter(employee_profile__city_name__icontains=city)

        skill = self.request.query_params.get('skill')
        if skill:
            queryset = queryset.filter(employee_profile__skill__id=skill)

        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(employee_profile__language__id=language)

        function = self.request.query_params.get('function')
        if function:
            queryset = queryset.filter(employee_profile__function__id=function)

        return queryset.distinct()

class VATValidationView(APIView):
    """
    View for validating VAT numbers and retrieving company details.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = VATValidationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = VATValidationService.validate_vat(
                serializer.validated_data['vat_number'],
                request.META.get('REMOTE_ADDR', '')
            )
            return Response(result, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)