from rest_framework import permissions
from drf_yasg import openapi

class BasePermission(permissions.BasePermission):
    """
    Base permission class with Swagger documentation.
    """
    swagger_security_definition = openapi.SecurityScheme(
        type=openapi.IN_HEADER,
        name='Authorization',
        scheme='bearer',
        bearerFormat='JWT',
        description='JWT token for authentication'
    )

    swagger_security_requirement = {
        'Bearer': []
    }

class IsOwner(BasePermission):
    """
    Permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the owner of the object.
        """
        return hasattr(obj, 'user') and obj.user == request.user

class IsEmployer(BasePermission):
    """
    Permission to only allow employers to access the view.
    """
    message = 'Must be an employer to perform this action.'

    def has_permission(self, request, view):
        """
        Check if user is an employer.
        """
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'employer_profile'))

class IsEmployee(BasePermission):
    """
    Permission to only allow employees to access the view.
    """
    message = 'Must be an employee to perform this action.'

    def has_permission(self, request, view):
        """
        Check if user is an employee.
        """
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'employee_profile'))

class ReadOnly(BasePermission):
    """
    Permission to only allow read-only access.
    """
    def has_permission(self, request, view):
        """
        Check if request is read-only.
        """
        return request.method in permissions.SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Permission to only allow admins to write, but allow anyone to read.
    """
    def has_permission(self, request, view):
        """
        Check if user is admin for write operations.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

class IsOwnerOrReadOnly(BasePermission):
    """
    Permission to only allow owners to write, but allow anyone to read.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check if user is owner for write operations.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(obj, 'user') and obj.user == request.user

class IsOwnerOrAdmin(BasePermission):
    """
    Permission to only allow owners or admins to access.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check if user is owner or admin.
        """
        return (
            request.user.is_staff or
            (hasattr(obj, 'user') and obj.user == request.user)
        )

# Permission combinations
class IsEmployerOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow employers to write, but allow anyone to read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'employer_profile'))

class IsEmployeeOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow employees to write, but allow anyone to read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'employee_profile'))

# Permission groups for common use cases
EMPLOYER_PERMISSIONS = [permissions.IsAuthenticated, IsEmployer]
EMPLOYEE_PERMISSIONS = [permissions.IsAuthenticated, IsEmployee]
OWNER_PERMISSIONS = [permissions.IsAuthenticated, IsOwner]
ADMIN_PERMISSIONS = [permissions.IsAuthenticated, permissions.IsAdminUser]
READ_ONLY_PERMISSIONS = [ReadOnly]