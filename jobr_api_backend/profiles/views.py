from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Education, WorkExperience, PortfolioItem
from .serializers import EducationSerializer, WorkExperienceSerializer, PortfolioItemSerializer
from .permissions import IsOwnerOrReadOnly, IsEmployeeUser

class EducationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing education entries.
    """
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated, IsEmployeeUser, IsOwnerOrReadOnly]

    @swagger_auto_schema(
        operation_description="List all education entries for the authenticated user",
        responses={200: EducationSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new education entry",
        request_body=EducationSerializer,
        responses={201: EducationSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific education entry",
        responses={200: EducationSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update an education entry",
        request_body=EducationSerializer,
        responses={200: EducationSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete an education entry",
        responses={204: "No content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return Education.objects.filter(employee=self.request.user.employee_profile)

class WorkExperienceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing work experience entries.
    """
    serializer_class = WorkExperienceSerializer
    permission_classes = [IsAuthenticated, IsEmployeeUser, IsOwnerOrReadOnly]

    @swagger_auto_schema(
        operation_description="List all work experience entries for the authenticated user",
        responses={200: WorkExperienceSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new work experience entry",
        request_body=WorkExperienceSerializer,
        responses={201: WorkExperienceSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific work experience entry",
        responses={200: WorkExperienceSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a work experience entry",
        request_body=WorkExperienceSerializer,
        responses={200: WorkExperienceSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a work experience entry",
        responses={204: "No content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return WorkExperience.objects.filter(employee=self.request.user.employee_profile)

class PortfolioViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing portfolio items.
    """
    serializer_class = PortfolioItemSerializer
    permission_classes = [IsAuthenticated, IsEmployeeUser, IsOwnerOrReadOnly]

    @swagger_auto_schema(
        operation_description="List all portfolio items for the authenticated user",
        responses={200: PortfolioItemSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new portfolio item",
        request_body=PortfolioItemSerializer,
        responses={201: PortfolioItemSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific portfolio item",
        responses={200: PortfolioItemSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a portfolio item",
        request_body=PortfolioItemSerializer,
        responses={200: PortfolioItemSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a portfolio item",
        responses={204: "No content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Increment view count for a portfolio item",
        responses={200: openapi.Response(
            description="View count incremented",
            examples={"application/json": {"status": "view count incremented"}}
        )}
    )
    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        portfolio_item = self.get_object()
        portfolio_item.view_count += 1
        portfolio_item.save()
        return Response({'status': 'view count incremented'})

    @swagger_auto_schema(
        operation_description="Toggle like for a portfolio item",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'liked': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether to like or unlike')
            }
        ),
        responses={200: openapi.Response(
            description="Like status updated",
            examples={"application/json": {"status": "like count updated"}}
        )}
    )
    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        portfolio_item = self.get_object()
        if request.data.get('liked', True):
            portfolio_item.like_count += 1
        else:
            portfolio_item.like_count = max(0, portfolio_item.like_count - 1)
        portfolio_item.save()
        return Response({'status': 'like count updated'})

    @swagger_auto_schema(
        operation_description="Get trending portfolio items",
        responses={200: PortfolioItemSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def trending(self, request):
        queryset = self.get_queryset().filter(is_public=True)
        trending_items = queryset.order_by('-view_count', '-like_count')
        page = self.paginate_queryset(trending_items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(trending_items, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Filter portfolio items by tag",
        manual_parameters=[
            openapi.Parameter(
                'tag',
                openapi.IN_QUERY,
                description="Tag to filter by",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: PortfolioItemSerializer(many=True),
            400: "Tag parameter is required"
        }
    )
    @action(detail=False, methods=['get'])
    def by_tag(self, request):
        tag = request.query_params.get('tag', None)
        if tag is None:
            return Response(
                {'error': 'Tag parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset().filter(tags__contains=[tag])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'employee_profile'):
            return PortfolioItem.objects.filter(employee=self.request.user.employee_profile)
        return PortfolioItem.objects.filter(is_public=True)
