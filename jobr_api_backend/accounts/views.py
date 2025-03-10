# accounts/views.py
from rest_framework import generics, status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import TokenService
from .serializers import (
    LoginSerializer,
    UserAuthenticationSerializer,
    ReviewSerializer,
    EmployeeStatisticsSerializer, 
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

    """
    A view to test the connection by returning the user's role.

    This view checks if the user is authenticated using JWT authentication and ensures the user has the required permissions to access this view.

    Attributes:
        authentication_classes (list): A list of authentication classes that define how the user is authenticated. In this case, JWT authentication.
        permission_classes (list): A list of permission classes to enforce access control. In this case, only authenticated users can access this view.

    Methods:
        get(self, request): Handles GET requests and returns a response with the user's role.

    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        """
        Handles GET requests to test the connection and return the authenticated user's role.

        Args:
        self (ConnectionTestView): The instance of the ConnectionTestView class.
        request (Request): The HTTP request object containing the user data.

        Returns:
        Response: A response containing the user's role.
        
        """

        return Response(
            {
                "role": request.user.role,
            }
        )


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserAuthenticationSerializer

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