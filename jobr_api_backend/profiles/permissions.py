from rest_framework import permissions
from accounts.models import ProfileOption

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        if request.user.role != ProfileOption.EMPLOYEE:
            return False
        return hasattr(request.user, 'employee_profile') and obj.employee == request.user.employee_profile

class IsEmployeeUser(permissions.BasePermission):
    """
    Custom permission to only allow employee users to access the view.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == ProfileOption.EMPLOYEE)

class IsEmployerUser(permissions.BasePermission):
    """
    Custom permission to only allow employer users to access the view.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == ProfileOption.EMPLOYER)