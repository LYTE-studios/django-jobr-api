from rest_framework import serializers
from drf_yasg import openapi

class SwaggerSerializerMixin:
    """
    Mixin to add Swagger documentation features to serializers.
    """
    @classmethod
    def add_swagger_documentation(cls, field_descriptions=None, required_fields=None):
        """
        Add Swagger documentation to serializer fields.
        
        Args:
            field_descriptions (dict): Mapping of field names to their descriptions
            required_fields (list): List of required field names
        """
        if not hasattr(cls, 'Meta'):
            cls.Meta = type('Meta', (), {})

        if not hasattr(cls.Meta, 'swagger_schema_fields'):
            cls.Meta.swagger_schema_fields = {}

        # Add field descriptions
        if field_descriptions:
            properties = {
                field_name: openapi.Schema(
                    type=cls._get_field_type(field_name),
                    description=description
                )
                for field_name, description in field_descriptions.items()
            }
            cls.Meta.swagger_schema_fields['properties'] = properties

        # Add required fields
        if required_fields:
            cls.Meta.swagger_schema_fields['required'] = required_fields

    @classmethod
    def _get_field_type(cls, field_name):
        """
        Get the OpenAPI type for a field.
        """
        field = cls._declared_fields.get(field_name)
        if isinstance(field, serializers.IntegerField):
            return openapi.TYPE_INTEGER
        elif isinstance(field, serializers.BooleanField):
            return openapi.TYPE_BOOLEAN
        elif isinstance(field, serializers.FloatField):
            return openapi.TYPE_NUMBER
        elif isinstance(field, serializers.ListField):
            return openapi.TYPE_ARRAY
        else:
            return openapi.TYPE_STRING

class BaseModelSerializer(SwaggerSerializerMixin, serializers.ModelSerializer):
    """
    Base serializer with Swagger documentation support.
    """
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_help_text_to_fields()

    def _add_help_text_to_fields(self):
        """
        Add model field help_text to serializer fields.
        """
        if not hasattr(self, 'Meta') or not hasattr(self.Meta, 'model'):
            return

        model = self.Meta.model
        for field_name, field in self.fields.items():
            model_field = model._meta.get_field(field_name)
            if hasattr(model_field, 'help_text') and model_field.help_text:
                field.help_text = model_field.help_text

class TimestampedSerializer(BaseModelSerializer):
    """
    Serializer for models with created_at and updated_at fields.
    """
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text="When this record was created"
    )
    updated_at = serializers.DateTimeField(
        read_only=True,
        help_text="When this record was last updated"
    )

    class Meta:
        abstract = True