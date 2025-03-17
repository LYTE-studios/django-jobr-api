from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q

class BaseFilterSet(filters.FilterSet):
    """
    Base filter set with Swagger documentation.
    """
    @classmethod
    def get_swagger_parameters(cls):
        """
        Get Swagger parameters for filter fields.
        """
        parameters = []
        for field_name, field in cls.base_filters.items():
            param = openapi.Parameter(
                name=field_name,
                in_=openapi.IN_QUERY,
                description=field.label or field_name,
                type=cls._get_swagger_type(field),
                required=field.required
            )
            parameters.append(param)
        return parameters

    @staticmethod
    def _get_swagger_type(field):
        """
        Get Swagger type for filter field.
        """
        if isinstance(field, filters.NumberFilter):
            return openapi.TYPE_NUMBER
        elif isinstance(field, filters.BooleanFilter):
            return openapi.TYPE_BOOLEAN
        elif isinstance(field, filters.DateTimeFilter):
            return openapi.TYPE_STRING
        else:
            return openapi.TYPE_STRING

class SearchableFilterMixin:
    """
    Mixin to add search functionality to filter sets.
    """
    search = filters.CharFilter(method='filter_search')
    
    def filter_search(self, queryset, name, value):
        """
        Search across specified fields.
        """
        if not hasattr(self.Meta, 'search_fields'):
            return queryset
        
        q_objects = Q()
        for field in self.Meta.search_fields:
            q_objects |= Q(**{f"{field}__icontains": value})
        return queryset.filter(q_objects)

    @classmethod
    def get_swagger_parameters(cls):
        """
        Add search parameter to Swagger documentation.
        """
        parameters = super().get_swagger_parameters()
        parameters.append(
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description='Search term',
                type=openapi.TYPE_STRING
            )
        )
        return parameters

class OrderableFilterMixin:
    """
    Mixin to add ordering functionality to filter sets.
    """
    ordering = filters.OrderingFilter()

    @classmethod
    def get_swagger_parameters(cls):
        """
        Add ordering parameter to Swagger documentation.
        """
        parameters = super().get_swagger_parameters()
        if hasattr(cls.Meta, 'ordering_fields'):
            parameters.append(
                openapi.Parameter(
                    'ordering',
                    openapi.IN_QUERY,
                    description='Order results by field (prefix with - for descending)',
                    type=openapi.TYPE_STRING,
                    enum=cls.Meta.ordering_fields
                )
            )
        return parameters

class DateRangeFilterMixin:
    """
    Mixin to add date range filtering functionality.
    """
    date_from = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='created_at', lookup_expr='lte')

    @classmethod
    def get_swagger_parameters(cls):
        """
        Add date range parameters to Swagger documentation.
        """
        parameters = super().get_swagger_parameters()
        parameters.extend([
            openapi.Parameter(
                'date_from',
                openapi.IN_QUERY,
                description='Start date (YYYY-MM-DD)',
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'date_to',
                openapi.IN_QUERY,
                description='End date (YYYY-MM-DD)',
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            )
        ])
        return parameters

class CommonFilterSet(SearchableFilterMixin, OrderableFilterMixin, DateRangeFilterMixin, BaseFilterSet):
    """
    Common filter set with search, ordering, and date range functionality.
    """
    class Meta:
        abstract = True