# accounts/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserSerializer, LoginSerializer, EmployeeSerializer, EmployerSerializer, AdminSerializer
from .models import CustomUser, Employee, Employer, Admin
from rest_framework.permissions import IsAuthenticated


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserLoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            return Response({"message": "Login successful", "user": user.username}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class EmployeeRegistration(generics.CreateAPIView):
    serializer_class = EmployeeSerializer

    def create(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            employee_data = request.data.copy()
            employee_data['user'] = user.id
            employee_serializer = self.get_serializer(data=employee_data)
            if employee_serializer.is_valid():
                employee_serializer.save()
                return Response({"success": True, "message": "Employee registered successfully."},
                                status=status.HTTP_201_CREATED)
            else:
                # delete user
                user.delete()
                return Response(employee_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployerRegistration(generics.CreateAPIView):
    serializer_class = EmployerSerializer

    def create(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            employer_data = request.data.copy()
            employer_data['user'] = user.id
            employer_serializer = self.get_serializer(data=employer_data)
            if employer_serializer.is_valid():
                employer_serializer.save()
                return Response({"success": True, "message": "Employer registered successfully."},
                                status=status.HTTP_201_CREATED)
            else:
                user.delete()
                return Response(employer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminRegistration(generics.CreateAPIView):
    serializer_class = AdminSerializer

    def create(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            admin_data = request.data.copy()
            admin_data['user'] = user.id
            admin_serializer = self.get_serializer(data=admin_data)
            if admin_serializer.is_valid():
                admin_serializer.save()
                return Response({"success": True, "message": "Admin registered successfully."},
                                status=status.HTTP_201_CREATED)
            else:
                user.delete()
                return Response(admin_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
