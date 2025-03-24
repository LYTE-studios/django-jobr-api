from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.exceptions import Throttled
from django.core.cache import cache
from unittest.mock import patch
from ..services import VATValidationService

class VATValidationServiceTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_valid_vat_format(self):
        """Test that valid BE VAT numbers pass format validation"""
        self.assertTrue(VATValidationService._validate_be_vat_format('BE0123456789'))
        self.assertTrue(VATValidationService._validate_be_vat_format('be0123456789'))

    def test_invalid_vat_format(self):
        """Test that invalid VAT numbers fail format validation"""
        invalid_formats = [
            'BE123',  # Too short
            'BE12345678901',  # Too long
            'FR0123456789',  # Wrong country code
            'BE12345678AB',  # Non-numeric
            'B0123456789',   # Missing country code
        ]
        for vat in invalid_formats:
            self.assertFalse(VATValidationService._validate_be_vat_format(vat))

    def test_rate_limiting(self):
        """Test that rate limiting works"""
        ip = '127.0.0.1'
        
        # Set requests count to limit
        cache.set(
            f"{VATValidationService.RATE_LIMIT_KEY_PREFIX}{ip}",
            VATValidationService.MAX_REQUESTS
        )

        with self.assertRaises(Throttled):
            VATValidationService._check_rate_limit(ip)

    @patch('requests.post')
    def test_validate_vat_integration(self, mock_post):
        """Test full VAT validation flow"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'valid': True}

        result = VATValidationService.validate_vat('BE0123456789', '127.0.0.1')
        
        self.assertTrue(result['is_valid'])
        self.assertIn('company_details', result)

    def test_caching(self):
        """Test that results are properly cached"""
        vat_number = 'BE0123456789'
        test_result = {
            'is_valid': True,
            'company_details': {
                'name': 'Test Company'
            }
        }

        # Cache a result
        VATValidationService._cache_result(vat_number, test_result)

        # Verify we can retrieve it
        cached = VATValidationService._get_cached_result(vat_number)
        self.assertEqual(cached, test_result)

    def tearDown(self):
        cache.clear()