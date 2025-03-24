from django.test import TestCase, override_settings
from rest_framework.exceptions import ValidationError, Throttled
from django.core.cache import cache
from unittest.mock import patch
from ..services import VATValidationService
from ..models import VATValidationResult, Employer, CustomUser

@override_settings(VATCHECKAPI_KEY='test_api_key')
class VATValidationServiceTests(TestCase):
    def setUp(self):
        cache.clear()
        VATValidationResult.objects.all().delete()
        self.user = CustomUser.objects.create(
            username='testemployer',
            email='test@example.com',
            role='employer'
        )
        self.employer = Employer.objects.create(
            user=self.user,
            company_name='Test Company'
        )

    def test_address_parsing(self):
        """Test address parsing functionality"""
        test_cases = [
            {
                "input": "Rijselsestraat 8, 8500 Kortrijk",
                "expected": {
                    "street_name": "Rijselsestraat",
                    "house_number": "8",
                    "postal_code": "8500",
                    "city": "Kortrijk"
                }
            },
            {
                "input": "Grote Markt 1, 1000 Brussel",
                "expected": {
                    "street_name": "Grote Markt",
                    "house_number": "1",
                    "postal_code": "1000",
                    "city": "Brussel"
                }
            },
            {
                "input": "Avenue Louise 123A, 1050 Ixelles",
                "expected": {
                    "street_name": "Avenue Louise",
                    "house_number": "123A",
                    "postal_code": "1050",
                    "city": "Ixelles"
                }
            }
        ]

        for case in test_cases:
            result = VATValidationService._parse_address(case["input"])
            self.assertEqual(result, case["expected"])

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

    @patch('requests.get')
    def test_validate_vat_success_and_storage(self, mock_get):
        """Test successful VAT validation with storage in database"""
        mock_response = {
            "valid": True,
            "country_code": "BE",
            "vat_number": "BE0123456789",
            "request_date": "2023-03-24",
            "name": "Test Company",
            "address": "Rijselsestraat 8, 8500 Kortrijk"
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        vat_number = 'BE0123456789'
        result = VATValidationService.validate_vat(vat_number, '127.0.0.1', self.employer)
        
        # Check API response
        self.assertTrue(result['is_valid'])
        self.assertEqual(result['company_details']['name'], "Test Company")
        self.assertEqual(result['company_details']['street_name'], "Rijselsestraat")
        self.assertEqual(result['company_details']['house_number'], "8")
        self.assertEqual(result['company_details']['postal_code'], "8500")
        self.assertEqual(result['company_details']['city'], "Kortrijk")
        self.assertEqual(result['company_details']['country'], "Belgium")

        # Verify database storage
        validation = VATValidationResult.objects.get(vat_number=vat_number)
        self.assertTrue(validation.is_valid)
        self.assertEqual(validation.company_name, "Test Company")
        self.assertEqual(validation.company_address, "Rijselsestraat 8, 8500 Kortrijk")
        self.assertEqual(validation.employer, self.employer)

        # Verify API is not called for subsequent validations
        result2 = VATValidationService.validate_vat(vat_number, '127.0.0.1')
        self.assertEqual(mock_get.call_count, 1)  # API should only be called once
        self.assertEqual(result2['company_details']['street_name'], "Rijselsestraat")
        self.assertEqual(result2['company_details']['house_number'], "8")
        self.assertEqual(result2['company_details']['postal_code'], "8500")
        self.assertEqual(result2['company_details']['city'], "Kortrijk")

    @patch('requests.get')
    def test_validate_nonexistent_vat_and_storage(self, mock_get):
        """Test validation and storage of non-existent VAT number"""
        mock_get.return_value.status_code = 404

        vat_number = 'BE0123456789'
        with self.assertRaises(ValidationError) as context:
            VATValidationService.validate_vat(vat_number, '127.0.0.1', self.employer)
        
        error_dict = context.exception.detail
        self.assertEqual(error_dict['error'], 'VAT_NOT_FOUND')

        # Verify invalid result is stored
        validation = VATValidationResult.objects.get(vat_number=vat_number)
        self.assertFalse(validation.is_valid)
        self.assertEqual(validation.employer, self.employer)

    @patch('requests.get')
    def test_validate_service_unavailable(self, mock_get):
        """Test handling of API service being unavailable"""
        mock_get.return_value.status_code = 500

        with self.assertRaises(ValidationError) as context:
            VATValidationService.validate_vat('BE0123456789', '127.0.0.1')
        
        error_dict = context.exception.detail
        self.assertEqual(error_dict['error'], 'SERVICE_UNAVAILABLE')
        self.assertEqual(error_dict['message'], 'VAT validation service is currently unavailable')

        # Verify no result is stored for service errors
        self.assertEqual(VATValidationResult.objects.count(), 0)

    @override_settings(VATCHECKAPI_KEY=None)
    def test_missing_api_key_configuration(self):
        """Test handling of missing API key configuration"""
        with self.assertRaises(ValidationError) as context:
            VATValidationService.validate_vat('BE0123456789', '127.0.0.1')
        
        error_dict = context.exception.detail
        self.assertEqual(error_dict['error'], 'SERVICE_UNAVAILABLE')
        self.assertEqual(error_dict['message'], 'VAT validation service is not properly configured')

    def test_database_caching(self):
        """Test that database results are used before API calls"""
        vat_number = 'BE0123456789'
        VATValidationResult.objects.create(
            vat_number=vat_number,
            is_valid=True,
            company_name='Database Company',
            company_address='Grote Markt 1, 1000 Brussel',
            employer=self.employer
        )

        with patch('requests.get') as mock_get:
            result = VATValidationService.validate_vat(vat_number, '127.0.0.1')
            mock_get.assert_not_called()  # API should not be called
            
            self.assertTrue(result['is_valid'])
            self.assertEqual(result['company_details']['name'], 'Database Company')
            self.assertEqual(result['company_details']['street_name'], 'Grote Markt')
            self.assertEqual(result['company_details']['house_number'], '1')
            self.assertEqual(result['company_details']['postal_code'], '1000')
            self.assertEqual(result['company_details']['city'], 'Brussel')

    def test_caching(self):
        """Test that results are properly cached"""
        vat_number = 'BE0123456789'
        test_result = {
            'is_valid': True,
            'company_details': {
                'name': 'Test Company',
                'street_name': 'Test Street',
                'house_number': '123',
                'city': 'Brussels',
                'postal_code': '1000',
                'country': 'Belgium'
            }
        }

        # Cache a result
        VATValidationService._cache_result(vat_number, test_result)

        # Verify we can retrieve it
        cached = VATValidationService._get_cached_result(vat_number)
        self.assertEqual(cached, test_result)

    def tearDown(self):
        cache.clear()
        VATValidationResult.objects.all().delete()