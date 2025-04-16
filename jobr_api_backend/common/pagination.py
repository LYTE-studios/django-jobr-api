from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class NoLimitPagination(PageNumberPagination):
    """
    Custom pagination class that returns all items in a single page
    while maintaining the standard pagination response structure.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    swagger_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'count': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Total number of items'
            ),
            'next': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_URI,
                description='URL to next page',
                nullable=True
            ),
            'previous': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_URI,
                description='URL to previous page',
                nullable=True
            ),
            'results': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT),
                description='List of items'
            ),
        }
    )

    swagger_parameters = [
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description='Page number',
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'page_size',
            openapi.IN_QUERY,
            description='Number of items per page',
            type=openapi.TYPE_INTEGER,
            default=10
        ),
    ]

    def get_paginated_response(self, data):
        """
        Return paginated response with standardized format.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def get_paginated_response_schema(self, schema):
        """
        Return schema for paginated response.
        """
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=OrderedDict([
                ('count', openapi.Schema(type=openapi.TYPE_INTEGER)),
                ('next', openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True)),
                ('previous', openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True)),
                ('results', schema),
            ])
        )

class LargePageNumberPagination(BasePageNumberPagination):
    """
    Pagination for large result sets.
    """
    page_size = 50
    max_page_size = 500

class SmallPageNumberPagination(BasePageNumberPagination):
    """
    Pagination for small result sets.
    """
    page_size = 5
    max_page_size = 20

class NoPagePagination(BasePageNumberPagination):
    """
    Pagination class that returns all results.
    Use with caution on large result sets.
    """
    page_size = None
    max_page_size = None

    def paginate_queryset(self, queryset, request, view=None):
        """
        Return all results without pagination.
        """
        return None

    def get_paginated_response(self, data):
        """
        Return unpaginated response.
        """
        return Response(data)

class CursorPaginationWithCount(PageNumberPagination):
    """
    Cursor pagination with total count for infinite scroll.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    cursor_query_param = 'cursor'

    def get_paginated_response(self, data):
        return Response({
            'count': len(data),
            'next': None,
            'previous': None,
            'results': data
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                },
                'results': schema,
            },
        }