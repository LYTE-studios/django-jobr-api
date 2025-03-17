from rest_framework.exceptions import APIException
from rest_framework import status
from drf_yasg import openapi

class BaseAPIException(APIException):
    """
    Base exception for API errors with Swagger documentation.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'
    default_code = 'error'

    # Swagger schema for error response
    swagger_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['error']),
            'message': openapi.Schema(type=openapi.TYPE_STRING),
            'code': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )

class ValidationError(BaseAPIException):
    """
    Exception for validation errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input.'
    default_code = 'validation_error'

    swagger_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['error']),
            'message': openapi.Schema(type=openapi.TYPE_STRING),
            'code': openapi.Schema(type=openapi.TYPE_STRING),
            'errors': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                additional_properties=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                )
            )
        }
    )

class NotFoundError(BaseAPIException):
    """
    Exception for resource not found errors.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'not_found'

class PermissionDeniedError(BaseAPIException):
    """
    Exception for permission denied errors.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permission denied.'
    default_code = 'permission_denied'

class AuthenticationError(BaseAPIException):
    """
    Exception for authentication errors.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication failed.'
    default_code = 'authentication_failed'

class ConflictError(BaseAPIException):
    """
    Exception for conflict errors.
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource conflict.'
    default_code = 'conflict'

class BadRequestError(BaseAPIException):
    """
    Exception for bad request errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request.'
    default_code = 'bad_request'

class ServiceUnavailableError(BaseAPIException):
    """
    Exception for service unavailable errors.
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable.'
    default_code = 'service_unavailable'

# Map of error types to their exception classes
ERROR_CLASSES = {
    'validation': ValidationError,
    'not_found': NotFoundError,
    'permission_denied': PermissionDeniedError,
    'authentication': AuthenticationError,
    'conflict': ConflictError,
    'bad_request': BadRequestError,
    'service_unavailable': ServiceUnavailableError,
}

def raise_error(error_type, detail=None, code=None):
    """
    Raise an API exception of the specified type.
    
    Args:
        error_type (str): Type of error (must be in ERROR_CLASSES)
        detail (str): Error message
        code (str): Error code
    """
    if error_type not in ERROR_CLASSES:
        raise ValueError(f"Unknown error type: {error_type}")
    
    exception_class = ERROR_CLASSES[error_type]
    raise exception_class(detail=detail, code=code)