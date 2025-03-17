from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, status
from rest_framework.response import Response

class SwaggerViewMixin:
    """
    Mixin to add Swagger documentation features to views.
    """
    @classmethod
    def add_swagger_documentation(cls, tags=None, operation_description=None):
        """
        Add Swagger documentation to view methods.
        
        Args:
            tags (list): List of tags for grouping endpoints
            operation_description (str): Description of the view operations
        """
        if not tags:
            tags = [cls.__module__.split('.')[0]]  # Use app name as default tag

        def decorator(func):
            return swagger_auto_schema(
                tags=tags,
                operation_description=operation_description
            )(func)
        return decorator

class BaseModelViewSet(SwaggerViewMixin, viewsets.ModelViewSet):
    """
    Base ViewSet with Swagger documentation support.
    """
    @swagger_auto_schema(
        operation_description="List all objects",
        responses={200: "List of objects with pagination"}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new object",
        responses={201: "Object created successfully"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific object",
        responses={200: "Object details", 404: "Object not found"}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update an object",
        responses={200: "Object updated successfully", 404: "Object not found"}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update an object",
        responses={200: "Object updated successfully", 404: "Object not found"}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete an object",
        responses={204: "Object deleted successfully", 404: "Object not found"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class PaginatedViewMixin:
    """
    Mixin to add pagination documentation to views.
    """
    pagination_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of items'),
            'next': openapi.Schema(type=openapi.TYPE_STRING, description='URL to next page', nullable=True),
            'previous': openapi.Schema(type=openapi.TYPE_STRING, description='URL to previous page', nullable=True),
            'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))
        }
    )

    def get_paginated_response_schema(self, schema):
        """
        Add pagination information to response schema.
        """
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                'results': schema
            }
        )

class ErrorResponseMixin:
    """
    Mixin to add common error responses to views.
    """
    error_responses = {
        400: 'Bad Request - Invalid input',
        401: 'Unauthorized - Authentication required',
        403: 'Forbidden - Insufficient permissions',
        404: 'Not Found - Resource does not exist',
        500: 'Internal Server Error'
    }

    def get_error_responses(self):
        """
        Get error response schemas for Swagger.
        """
        return {
            status_code: openapi.Response(
                description=description,
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description=description
                        )
                    }
                )
            )
            for status_code, description in self.error_responses.items()
        }
