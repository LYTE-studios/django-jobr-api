# accounts/views.py
from rest_framework import generics, status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import TokenService
from .serializers import (
    LoginSerializer,
    EmployeeSerializer,
    EmployerSerializer,
    AdminSerializer,
    ReviewSerializer,
    EmployeeStatisticsSerializer, 
    UserGallerySerializer,
    UserGalleryUpdateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.http import Http404
from firebase_admin import auth as firebase_auth
import google.auth.transport.requests
import google.oauth2.id_token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import CustomUser, Employee, Employer, UserGallery
from .serializers import UserSerializer


class ConnectionTestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "role": request.user.role,
            }
        )


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = TokenService.get_tokens_for_user(user)

        return Response(
            {"access": tokens["access"], "refresh": tokens["refresh"]},
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "message": "Login successful",
                        "user": "username",
                        "access": "access_token_string",
                        "refresh": "refresh_token_string",
                    }
                },
            )
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = TokenService.get_tokens_for_user(user)

        return Response(
            {
                "message": "Login successful",
                "user": user.username,
                "role": user.role,
                "access": tokens["access"],
                "refresh": tokens["refresh"],
            },
            status=status.HTTP_200_OK,
        )


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class EmployeeRegistration(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeSerializer

    @swagger_auto_schema(
        responses={
            201: openapi.Response(
                description="Employee registration successful",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Employee registered successfully.",
                        "access": "access_token_string",
                        "refresh": "refresh_token_string",
                    }
                },
            )
        }
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role != "employee":
            return Response(
                {"error": "User is not allowed to register as an employee."},
                status=status.HTTP_403_FORBIDDEN,
            )

        employee_data = request.data.copy()
        employee_data["user"] = user.id
        employee_serializer = self.get_serializer(data=employee_data)
        if employee_serializer.is_valid():
            employee_serializer.save()
            return Response(
                {"success": True, "message": "Employee registered successfully."}
                | TokenService.get_tokens_for_user(user),
                status=status.HTTP_201_CREATED,
            )
        return Response(employee_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployerRegistration(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployerSerializer

    @swagger_auto_schema(
        responses={
            201: openapi.Response(
                description="Employer registration successful",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Employer registered successfully.",
                        "access": "access_token_string",
                        "refresh": "refresh_token_string",
                    }
                },
            )
        }
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role != "employer":
            return Response(
                {"error": "User is not allowed to register as an employer."},
                status=status.HTTP_403_FORBIDDEN,
            )

        employer_data = request.data.copy()
        employer_data["user"] = user.id
        employer_serializer = self.get_serializer(data=employer_data)
        if employer_serializer.is_valid():
            employer_serializer.save()
            return Response(
                {"success": True, "message": "Employer registered successfully."}
                | TokenService.get_tokens_for_user(user),
                status=status.HTTP_201_CREATED,
            )
        return Response(employer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminRegistration(generics.CreateAPIView):
    serializer_class = AdminSerializer

    @swagger_auto_schema(
        responses={
            201: openapi.Response(
                description="Admin registration successful",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Admin registered successfully.",
                        "access": "access_token_string",
                        "refresh": "refresh_token_string",
                    }
                },
            )
        }
    )
    def create(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            admin_data = request.data.copy()
            admin_data["user"] = user.id
            admin_serializer = self.get_serializer(data=admin_data)
            if admin_serializer.is_valid():
                admin_serializer.save()
                return Response(
                    {"success": True, "message": "Admin registered successfully."}
                    | TokenService.get_tokens_for_user(user),
                    status=status.HTTP_201_CREATED,
                )
            else:
                user.delete()
                return Response(
                    admin_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleSignInView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Google Login successful",
                examples={
                    "application/json": {
                        "message": "Google Login successful",
                        "created": "01/01/2000 00:00:00",
                        "user": "username",
                        "access": "access_token_string",
                        "refresh": "refresh_token_string",
                    }
                },
            )
        }
    )
    def post(self, request):
        try:
            # Get the ID token from the request
            id_token = request.data.get("id_token")

            if not id_token:
                return Response(
                    {"error": "ID token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verify Google ID token
            request_google = google.auth.transport.requests.Request()
            try:
                id_info = google.oauth2.id_token.verify_firebase_token(
                    id_token, request_google, settings.GOOGLE_CLIENT_ID
                )
            except ValueError as e:
                return Response(
                    {"error": "Invalid token", "details": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract user information
            email = id_info.get("email")
            name = id_info.get("name", "")

            # Check if user exists, if not create
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "first_name": name.split()[0] if name else "",
                    "last_name": name.split()[-1] if len(name.split()) > 1 else "",
                },
            )

            # Return response
            return Response(
                {
                    "message": "Google Login successful",
                    "user": user.username,
                    "created": created,
                }
                | TokenService.get_tokens_for_user(user),
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Google Authentication failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AppleSignInView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Apple Login successful",
                examples={
                    "application/json": {
                        "message": "Apple Login successful",
                        "created": "01/01/2000 00:00:00",
                        "user": "username",
                        "access": "access_token_string",
                        "refresh": "refresh_token_string",
                    }
                },
            )
        }
    )
    def post(self, request):
        try:
            # Get the ID token from the request
            id_token = request.data.get("id_token")

            if not id_token:
                return Response(
                    {"error": "ID token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verify Apple ID token using Firebase
            try:
                decoded_token = firebase_auth.verify_id_token(id_token)
            except (ValueError, firebase_auth.InvalidIdTokenError) as e:
                return Response(
                    {"error": "Invalid token", "details": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract user information
            email = decoded_token.get("email")
            apple_uid = decoded_token.get("uid")

            # Check if user exists, if not create
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    "username": f"apple_{apple_uid}",
                },
            )

            # Return response
            return Response(
                {
                    "message": "Apple Login successful",
                    "user": user.username,
                    "created": created,
                }
                | TokenService.get_tokens_for_user(user),
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Apple Authentication failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  # Allow anyone to post a review

    def perform_create(self, serializer):
        user = self.request.user

        # Determine reviewer type and save accordingly
        if hasattr(user, "employee"):
            reviewer_type = "employee"
            serializer.save(employee=user.employee, reviewer_type=reviewer_type)
        elif hasattr(user, "employer"):
            reviewer_type = "employer"
            serializer.save(employer=user.employer, reviewer_type=reviewer_type)
        else:
            # For anonymous users
            reviewer_type = "anonymous"
            serializer.save(reviewer_type=reviewer_type)

class EmployeeStatisticsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Get the Employee instance for the current user
            employee = Employee.objects.get(user=request.user)
            serializer = EmployeeStatisticsSerializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            employee = Employee.objects.get(user=request.user)
            employee.phone_session_counts += 1
            employee.save()

            serializer = EmployeeStatisticsSerializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class AISuggestionsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return CustomUser.objects.filter(role="employee")


class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class AllUserGalleriesView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get_queryset(self):
        return CustomUser.objects.all().prefetch_related("users_gallery")

class UserByUserView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get_object(self):
        try:
            return CustomUser.objects.get(id=self.kwargs["pk"])
        except CustomUser.DoesNotExist:
            raise Http404("User does not exist")

    def get_queryset(self):
        return CustomUser.objects.prefetch_related("users_gallery")


class UpdateUserGalleryView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ["put"]

    def put(self, request):
        serializer = UserGalleryUpdateSerializer(
            data=request.data, context={"user": request.user.id}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        user_id = request.user.id
        gallery_image = validated_data.get("gallery")

        user = CustomUser.objects.get(id=user_id)
        UserGallery.objects.filter(user=user).delete()
        for image in gallery_image:
            UserGallery.objects.create(user=user, gallery=image)

        serializer = UserSerializer(
            CustomUser.objects.prefetch_related("users_gallery").get(pk=user.id)
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteUserGallery(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            employer = CustomUser.objects.get(id=request.user.id)
            UserGallery.objects.filter(user=employer).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Employer.DoesNotExist:
            return Response(
                {"details": "Current user isn't an User"},
                status=status.HTTP_404_NOT_FOUND,
            )


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({"detail": "Account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)