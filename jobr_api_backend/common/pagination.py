from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class NoLimitPagination(PageNumberPagination):
    """
    Custom pagination class that returns all items in a single page
    while maintaining the standard pagination response structure.
    """
    page_size = None  # No limit on page size

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