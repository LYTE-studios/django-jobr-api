from rest_framework import viewsets, permissions, mixins
from rest_framework.viewsets import GenericViewSet
from .models import AISuggestion
from .serializers import AISuggestionSerializer


class AISuggestionViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         GenericViewSet):
    """
    ViewSet for viewing AI suggestions.
    Create, update, and delete operations are not allowed as suggestions
    are generated automatically by the system.
    """
    queryset = AISuggestion.objects.all()
    serializer_class = AISuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter suggestions based on the user's role.
        """
        user = self.request.user
        queryset = AISuggestion.objects.all()

        if user.role == 'employee':
            return queryset.filter(employee__user=user)
        elif user.role == 'employer':
            return queryset.filter(vacancy__company__user=user)
        elif user.is_staff:
            return queryset
        
        return AISuggestion.objects.none()
