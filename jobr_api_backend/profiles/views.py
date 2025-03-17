from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Education, WorkExperience, PortfolioItem
from .serializers import EducationSerializer, WorkExperienceSerializer, PortfolioItemSerializer
from .permissions import IsOwnerOrReadOnly, IsEmployeeUser

class EducationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing education instances.
    """
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated, IsEmployeeUser, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        This view should return a list of all education entries
        for the currently authenticated user.
        """
        return Education.objects.filter(employee=self.request.user.employee_profile)

class WorkExperienceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing work experience instances.
    """
    serializer_class = WorkExperienceSerializer
    permission_classes = [IsAuthenticated, IsEmployeeUser, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        This view should return a list of all work experience entries
        for the currently authenticated user.
        """
        return WorkExperience.objects.filter(employee=self.request.user.employee_profile)

class PortfolioViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing portfolio items.
    """
    serializer_class = PortfolioItemSerializer
    permission_classes = [IsAuthenticated, IsEmployeeUser, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Return all public portfolio items or all items for the owner.
        """
        if self.request.user.is_authenticated and hasattr(self.request.user, 'employee_profile'):
            return PortfolioItem.objects.filter(employee=self.request.user.employee_profile)
        return PortfolioItem.objects.filter(is_public=True)

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        """
        Increment the view count for a portfolio item.
        """
        portfolio_item = self.get_object()
        portfolio_item.view_count += 1
        portfolio_item.save()
        return Response({'status': 'view count incremented'})

    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        """
        Toggle like for a portfolio item.
        """
        portfolio_item = self.get_object()
        if request.data.get('liked', True):
            portfolio_item.like_count += 1
        else:
            portfolio_item.like_count = max(0, portfolio_item.like_count - 1)
        portfolio_item.save()
        return Response({'status': 'like count updated'})

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """
        Get trending portfolio items based on views and likes.
        """
        queryset = self.get_queryset().filter(is_public=True)
        # Order by a combination of views and likes
        trending_items = queryset.order_by('-view_count', '-like_count')
        page = self.paginate_queryset(trending_items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(trending_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_tag(self, request):
        """
        Filter portfolio items by tag.
        """
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
