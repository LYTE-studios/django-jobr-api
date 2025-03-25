from django.test import TestCase
from ..services import VATValidationService

class AddressParsingTests(TestCase):
    def test_address_parsing(self):
        test_cases = [
            # Newline format
            {
                "input": "Rijselsestraat 8\n8500 Kortrijk",
                "expected": {
                    "street_name": "Rijselsestraat",
                    "house_number": "8",
                    "postal_code": "8500",
                    "city": "Kortrijk"
                }
            },
            # Standard format
            {
                "input": "Rijselsestraat 8, 8500 Kortrijk",
                "expected": {
                    "street_name": "Rijselsestraat",
                    "house_number": "8",
                    "postal_code": "8500",
                    "city": "Kortrijk"
                }
            },
            # With bus number
            {
                "input": "Nieuwstraat 12 bus 3, 2000 Antwerpen",
                "expected": {
                    "street_name": "Nieuwstraat",
                    "house_number": "12 bus 3",
                    "postal_code": "2000",
                    "city": "Antwerpen"
                }
            },
            # With house number suffix
            {
                "input": "Avenue Louise 123A, 1050 Ixelles",
                "expected": {
                    "street_name": "Avenue Louise",
                    "house_number": "123A",
                    "postal_code": "1050",
                    "city": "Ixelles"
                }
            },
            # With range
            {
                "input": "Brusselsestraat 10-12, 2800 Mechelen",
                "expected": {
                    "street_name": "Brusselsestraat",
                    "house_number": "10-12",
                    "postal_code": "2800",
                    "city": "Mechelen"
                }
            },
            # Multi-word street name
            {
                "input": "Prins van Luiklaan 24, 1070 Anderlecht",
                "expected": {
                    "street_name": "Prins van Luiklaan",
                    "house_number": "24",
                    "postal_code": "1070",
                    "city": "Anderlecht"
                }
            }
        ]

        for test_case in test_cases:
            result = VATValidationService._parse_address(test_case["input"])
            self.assertEqual(
                result,
                test_case["expected"],
                f"Failed to parse address: {test_case['input']}"
            )