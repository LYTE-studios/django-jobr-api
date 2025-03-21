from django.test import TestCase
from django.urls import reverse
from rest_framework import serializers, viewsets
from rest_framework.test import APIRequestFactory
from unittest.mock import patch, MagicMock
from drf_yasg import openapi
from common.views import (
    SwaggerViewMixin, BaseModelViewSet, PaginatedViewMixin,
    ErrorResponseMixin
)
from django.db import models

# Test Models and Serializers
class TestModel(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'common'

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestModel
        fields = ['id', 'name']

class TestViewSet(BaseModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestSerializer

class SwaggerViewMixinTests(TestCase):
    def test_add_swagger_documentation_with_default_tags(self):
        """Test swagger documentation with default tags"""
        @SwaggerViewMixin.add_swagger_documentation()
        def test_view():
            pass

        # Check if swagger_auto_schema was applied with correct tags
        self.assertTrue(hasattr(test_view, '_swagger_auto_schema'))
        schema = getattr(test_view, '_swagger_auto_schema')
        self.assertEqual(schema['tags'], ['common'])

    def test_add_swagger_documentation_with_custom_tags(self):
        """Test swagger documentation with custom tags"""
        @SwaggerViewMixin.add_swagger_documentation(tags=['custom'])
        def test_view():
            pass

        schema = getattr(test_view, '_swagger_auto_schema')
        self.assertEqual(schema['tags'], ['custom'])

    def test_add_swagger_documentation_with_description(self):
        """Test swagger documentation with operation description"""
        @SwaggerViewMixin.add_swagger_documentation(operation_description='Test description')
        def test_view():
            pass

        schema = getattr(test_view, '_swagger_auto_schema')
        self.assertEqual(schema['operation_description'], 'Test description')

class BaseModelViewSetTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.viewset = TestViewSet()

    def test_list_swagger_documentation(self):
        """Test list method swagger documentation"""
        schema = getattr(self.viewset.list, '_swagger_auto_schema')
        self.assertEqual(schema['operation_description'], 'List all objects')
        self.assertEqual(schema['responses'][200], 'List of objects with pagination')

    def test_create_swagger_documentation(self):
        """Test create method swagger documentation"""
        schema = getattr(self.viewset.create, '_swagger_auto_schema')
        self.assertEqual(schema['operation_description'], 'Create a new object')
        self.assertEqual(schema['responses'][201], 'Object created successfully')

    def test_retrieve_swagger_documentation(self):
        """Test retrieve method swagger documentation"""
        schema = getattr(self.viewset.retrieve, '_swagger_auto_schema')
        self.assertEqual(schema['operation_description'], 'Retrieve a specific object')
        self.assertEqual(schema['responses'][200], 'Object details')
        self.assertEqual(schema['responses'][404], 'Object not found')

class PaginatedViewMixinTests(TestCase):
    def setUp(self):
        self.mixin = PaginatedViewMixin()

    def test_pagination_schema(self):
        """Test pagination schema structure"""
        schema = self.mixin.pagination_schema
        self.assertEqual(schema.type, openapi.TYPE_OBJECT)
        self.assertIn('count', schema.properties)
        self.assertIn('next', schema.properties)
        self.assertIn('previous', schema.properties)
        self.assertIn('results', schema.properties)

    def test_get_paginated_response_schema(self):
        """Test paginated response schema generation"""
        test_schema = openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_OBJECT)
        )
        response_schema = self.mixin.get_paginated_response_schema(test_schema)
        
        self.assertEqual(response_schema.type, openapi.TYPE_OBJECT)
        self.assertIn('count', response_schema.properties)
        self.assertIn('next', response_schema.properties)
        self.assertIn('previous', response_schema.properties)
        self.assertIn('results', response_schema.properties)
        self.assertEqual(response_schema.properties['results'], test_schema)

class ErrorResponseMixinTests(TestCase):
    def setUp(self):
        self.mixin = ErrorResponseMixin()

    def test_error_responses_structure(self):
        """Test error responses dictionary structure"""
        self.assertIn(400, self.mixin.error_responses)
        self.assertIn(401, self.mixin.error_responses)
        self.assertIn(403, self.mixin.error_responses)
        self.assertIn(404, self.mixin.error_responses)
        self.assertIn(500, self.mixin.error_responses)

    def test_get_error_responses(self):
        """Test error response schema generation"""
        error_schemas = self.mixin.get_error_responses()
        
        # Test 400 error schema
        bad_request_schema = error_schemas[400]
        self.assertEqual(bad_request_schema.description, 'Bad Request - Invalid input')
        self.assertIsInstance(bad_request_schema.schema, openapi.Schema)
        self.assertEqual(bad_request_schema.schema.type, openapi.TYPE_OBJECT)
        self.assertIn('error', bad_request_schema.schema.properties)

        # Test structure of error property
        error_property = bad_request_schema.schema.properties['error']
        self.assertEqual(error_property.type, openapi.TYPE_STRING)
        self.assertEqual(error_property.description, 'Bad Request - Invalid input')