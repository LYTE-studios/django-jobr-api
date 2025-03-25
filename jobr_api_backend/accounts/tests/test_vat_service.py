from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from ..models import CustomUser, VATValidationResult
import json

class VATValidationViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('validate-vat')
        
        # Mock settings
        from django.test import override_settings
        self.settings_patcher = override_settings(
            VATCHECKAPI_KEY='test_api_key'
        )
        self.settings_patcher.enable()

    def tearDown(self):
        self.settings_patcher.disable()

    @patch('requests.get')
    def test_vat_validation_address_parsing(self, mock_get):
        # Mock the API response
        mock_response = {
            "valid": True,
            "name": "Test Company BV",
            "address": "Nieuwstraat 12 bus 3, 2000 Antwerpen",
            "vat_number": "BE0123456789"
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Make the request
        response = self.client.post(
            self.url,
            data={'vat_number': 'BE0123456789'},
            REMOTE_ADDR='127.0.0.1'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify the address is properly parsed
        self.assertEqual(data['company_details'], {
            'name': 'Test Company BV',
            'street_name': 'Nieuwstraat',
            'house_number': '12 bus 3',
            'postal_code': '2000',
            'city': 'Antwerpen',
            'country': 'Belgium'
        })

        # Test with a different address format
        mock_response = {
            "valid": True,
            "name": "Test Company BV",
            "address": "Avenue Louise 123A, 1050 Ixelles",
            "vat_number": "BE0123456789"
        }
        mock_get.return_value.json.return_value = mock_response

        response = self.client.post(
            self.url,
            data={'vat_number': 'BE9876543210'},
            REMOTE_ADDR='127.0.0.1'
        )
        data = response.json()
        
        self.assertEqual(data['company_details'], {
            'name': 'Test Company BV',
            'street_name': 'Avenue Louise',
            'house_number': '123A',
            'postal_code': '1050',
            'city': 'Ixelles',
            'country': 'Belgium'
        })

        # Test with newline in address
        mock_response = {
            "valid": True,
            "name": "Test Company BV",
            "address": "Rijselsestraat 8\n8500 Kortrijk",
            "vat_number": "BE0123456789"
        }
        mock_get.return_value.json.return_value = mock_response

        response = self.client.post(
            self.url,
            data={'vat_number': 'BE7777777777'},
            REMOTE_ADDR='127.0.0.1'
        )
        data = response.json()
        
        self.assertEqual(data['company_details'], {
            'name': 'Test Company BV',
            'street_name': 'Rijselsestraat',
            'house_number': '8',
            'postal_code': '8500',
            'city': 'Kortrijk',
            'country': 'Belgium'
        })

        # Test with a range in house number
        mock_response = {
            "valid": True,
            "name": "Test Company BV",
            "address": "Brusselsestraat 10-12, 2800 Mechelen",
            "vat_number": "BE0123456789"
        }
        mock_get.return_value.json.return_value = mock_response

        response = self.client.post(
            self.url,
            data={'vat_number': 'BE5555555555'},
            REMOTE_ADDR='127.0.0.1'
        )
        data = response.json()
        
        self.assertEqual(data['company_details'], {
            'name': 'Test Company BV',
            'street_name': 'Brusselsestraat',
            'house_number': '10-12',
            'postal_code': '2800',
            'city': 'Mechelen',
            'country': 'Belgium'
        })

    @patch('requests.get')
    @patch('django.core.cache.cache.get')
    @patch('django.core.cache.cache.set')
    def test_vat_validation_caching(self, mock_cache_set, mock_cache_get, mock_get):
        # Setup mock API response
        mock_response = {
            "valid": True,
            "name": "Test Company BV",
            "address": "Nieuwstraat 12 bus 3, 2000 Antwerpen",
            "vat_number": "BE0123456789"
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        
        # First request - no cache
        mock_cache_get.return_value = None
        response = self.client.post(
            self.url,
            data={'vat_number': 'BE0123456789'},
            REMOTE_ADDR='127.0.0.1'
        )
        if response.status_code != status.HTTP_200_OK:
            print("Response content:", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get.assert_called_once()
        # Verify cache was set for both rate limiting and VAT validation result
        print("Cache set calls:", mock_cache_set.call_args_list)
        self.assertEqual(mock_cache_set.call_count, 3)  # Update expected count to 3
        # First call should be for rate limiting
        self.assertTrue(mock_cache_set.call_args_list[0][0][0].startswith('vat_validation_ratelimit_'))
        # Second call should be for VAT validation result
        self.assertTrue(mock_cache_set.call_args_list[1][0][0].startswith('vat_validation_BE'))

        # Reset mocks
        mock_get.reset_mock()
        mock_cache_set.reset_mock()

        # Second request - should use cache
        expected_result = {
            'is_valid': True,
            'company_details': {
                'name': 'Test Company BV',
                'street_name': 'Nieuwstraat',
                'house_number': '12 bus 3',
                'postal_code': '2000',
                'city': 'Antwerpen',
                'country': 'Belgium'
            }
        }
        mock_cache_get.return_value = expected_result
        
        response = self.client.post(
            self.url,
            data={'vat_number': 'BE0123456789'},
            REMOTE_ADDR='127.0.0.1'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_result)
        
        # Verify API wasn't called again
        mock_get.assert_not_called()

    @patch('requests.get')
    @patch('django.core.cache.cache.get')
    def test_vat_validation_database_storage(self, mock_cache_get, mock_get):
        # Ensure no cache hit
        mock_cache_get.return_value = None
        mock_response = {
            "valid": True,
            "name": "Test Company BV",
            "address": "Nieuwstraat 12 bus 3, 2000 Antwerpen",
            "vat_number": "BE0123456789"
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Make request
        response = self.client.post(
            self.url,
            data={'vat_number': 'BE0123456789'},
            REMOTE_ADDR='127.0.0.1'
        )
        if response.status_code != status.HTTP_200_OK:
            print("Response content:", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify database storage
        validation_result = VATValidationResult.objects.get(vat_number='BE0123456789')
        self.assertEqual(validation_result.company_name, 'Test Company BV')
        self.assertEqual(validation_result.company_address, 'Nieuwstraat 12 bus 3, 2000 Antwerpen')
        self.assertTrue(validation_result.is_valid)

        # Verify the parsed address in response
        data = response.json()
        self.assertEqual(data['company_details'], {
            'name': 'Test Company BV',
            'street_name': 'Nieuwstraat',
            'house_number': '12 bus 3',
            'postal_code': '2000',
            'city': 'Antwerpen',
            'country': 'Belgium'
        })