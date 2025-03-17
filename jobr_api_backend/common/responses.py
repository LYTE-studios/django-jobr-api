from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi

class APIResponse:
    """
    Standard API response formats with Swagger documentation.
    """
    # Swagger schemas for common responses
    SUCCESS_SCHEMA = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['success']),
            'message': openapi.Schema(type=openapi.TYPE_STRING),
            'data': openapi.Schema(type=openapi.TYPE_OBJECT),
        }
    )

    ERROR_SCHEMA = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['error']),
            'message': openapi.Schema(type=openapi.TYPE_STRING),
            'errors': openapi.Schema(type=openapi.TYPE_OBJECT),
        }
    )

    PAGINATION_SCHEMA = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'count': openapi.Schema(type=openapi.TYPE_INTEGER),
            'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
            'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
            'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )

    @staticmethod
    def success(data=None, message=None, status_code=status.HTTP_200_OK):
        """
        Success response with optional data and message.
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code (default: 200)
        """
        response = {
            'status': 'success'
        }
        if message:
            response['message'] = message
        if data is not None:
            response['data'] = data
        return Response(response, status=status_code)

    @staticmethod
    def error(message, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """
        Error response with message and optional error details.
        
        Args:
            message: Error message
            errors: Detailed error information
            status_code: HTTP status code (default: 400)
        """
        response = {
            'status': 'error',
            'message': message
        }
        if errors is not None:
            response['errors'] = errors
        return Response(response, status=status_code)

    @staticmethod
    def paginated_response(paginator, data, message=None):
        """
        Paginated response with optional message.
        
        Args:
            paginator: DRF paginator instance
            data: Serialized data
            message: Optional message
        """
        response = {
            'status': 'success',
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': data
        }
        if message:
            response['message'] = message
        return Response(response)

    # Common response documentation
    COMMON_RESPONSES = {
        200: openapi.Response(
            description="Success response",
            schema=SUCCESS_SCHEMA
        ),
        400: openapi.Response(
            description="Bad request",
            schema=ERROR_SCHEMA
        ),
        401: openapi.Response(
            description="Unauthorized - Authentication required",
            schema=ERROR_SCHEMA
        ),
        403: openapi.Response(
            description="Forbidden - Insufficient permissions",
            schema=ERROR_SCHEMA
        ),
        404: openapi.Response(
            description="Not found",
            schema=ERROR_SCHEMA
        ),
        500: openapi.Response(
            description="Internal server error",
            schema=ERROR_SCHEMA
        )
    }

    # Common response examples
    RESPONSE_EXAMPLES = {
        'success': {
            'status': 'success',
            'message': 'Operation completed successfully',
            'data': {'example': 'data'}
        },
        'error': {
            'status': 'error',
            'message': 'An error occurred',
            'errors': {'field': ['Error detail']}
        },
        'paginated': {
            'status': 'success',
            'count': 100,
            'next': 'http://api.example.org/accounts/?page=2',
            'previous': None,
            'results': [{'example': 'data'}]
        }
    }