from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class NoLimitPagination(PageNumberPagination):
    """
    Custom pagination class that returns all items in a single page
    while maintaining the standard pagination response structure.
    """
    page_size = None  # No limit on page size

    def paginate_queryset(self, queryset, request, view=None):
        self.count = queryset.count()
        return list(queryset)

    def get_paginated_response(self, data):
        return Response({
            'count': self.count,
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