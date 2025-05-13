from rest_framework import serializers
from .models import AISuggestion


class AISuggestionSerializer(serializers.ModelSerializer):
    """
    Serializer for AI suggestions.
    """
    class Meta:
        model = AISuggestion
        fields = [
            'id',
            'employee',
            'vacancy',
            'quantitative_score',
            'qualitative_score',
            'total_score',
            'message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'quantitative_score',
            'qualitative_score',
            'total_score',
            'message',
            'created_at',
            'updated_at',
        ]