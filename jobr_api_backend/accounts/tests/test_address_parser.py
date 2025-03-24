from django.test import TestCase
from ..services import VATValidationService

class AddressParserTests(TestCase):
    """Test suite for the address parsing functionality."""

    def test_standard_address(self):
        """Test parsing of standard address format."""
        address = "Rijselsestraat 8, 8500 Kortrijk"
        result = VATValidationService._parse_address(address)
        self.assertEqual(result, {
            "street_name": "Rijselsestraat",
            "house_number": "8",
            "postal_code": "8500",
            "city": "Kortrijk"
        })

    def test_address_with_house_number_suffix(self):
        """Test parsing address with house number suffix."""
        address = "Avenue Louise 123A, 1050 Ixelles"
        result = VATValidationService._parse_address(address)
        self.assertEqual(result, {
            "street_name": "Avenue Louise",
            "house_number": "123A",
            "postal_code": "1050",
            "city": "Ixelles"
        })

    def test_address_with_bus_number(self):
        """Test parsing address with bus/box number."""
        address = "Nieuwstraat 12 bus 3, 2000 Antwerpen"
        result = VATValidationService._parse_address(address)
        self.assertEqual(result, {
            "street_name": "Nieuwstraat",
            "house_number": "12 bus 3",
            "postal_code": "2000",
            "city": "Antwerpen"
        })

    def test_address_with_multiple_word_street(self):
        """Test parsing address with multi-word street name."""
        address = "Prins van Luiklaan 24, 1070 Anderlecht"
        result = VATValidationService._parse_address(address)
        self.assertEqual(result, {
            "street_name": "Prins van Luiklaan",
            "house_number": "24",
            "postal_code": "1070",
            "city": "Anderlecht"
        })

    def test_address_with_multiple_word_city(self):
        """Test parsing address with multi-word city name."""
        address = "Stationsstraat 1, 3090 Overijse Hoeilaart"
        result = VATValidationService._parse_address(address)
        self.assertEqual(result, {
            "street_name": "Stationsstraat",
            "house_number": "1",
            "postal_code": "3090",
            "city": "Overijse Hoeilaart"
        })

    def test_address_with_special_characters(self):
        """Test parsing address with special characters."""
        address = "Chaussée d'Ixelles 15-17, 1050 Bruxelles"
        result = VATValidationService._parse_address(address)
        self.assertEqual(result, {
            "street_name": "Chaussée d'Ixelles",
            "house_number": "15-17",
            "postal_code": "1050",
            "city": "Bruxelles"
        })

    def test_address_without_house_number(self):
        """Test parsing address without house number."""
        address = "Grote Markt, 1000 Brussel"
        result = VATValidationService._parse_address(address)
        self.assertEqual(result, {
            "street_name": "Grote Markt",
            "house_number": "",
            "postal_code": "1000",
            "city": "Brussel"
        })

    def test_address_without_postal_code(self):
        """Test parsing address without postal code."""
        address = "Kerkstraat 45, Gent"
        result = VATValidationService._parse_address(address)
        self.assertEqual(result, {
            "street_name": "Kerkstraat",
            "house_number": "45",
            "postal_code": "",
            "city": "Gent"
        })

    def test_address_with_extra_spaces(self):
        """Test parsing address with extra spaces."""
        address = "  Leuvensesteenweg   123 ,  3000   Leuven  "
        result = VATValidationService._parse_address(address)
        self.assertEqual(result, {
            "street_name": "Leuvensesteenweg",
            "house_number": "123",
            "postal_code": "3000",
            "city": "Leuven"
        })

    def test_address_with_range_house_numbers(self):
        """Test parsing address with range of house numbers."""
        address = "Brusselsestraat 10-12, 2800 Mechelen"
        result = VATValidationService._parse_address(address)
        self.assertEqual(result, {
            "street_name": "Brusselsestraat",
            "house_number": "10-12",
            "postal_code": "2800",
            "city": "Mechelen"
        })

    def test_address_with_letter_in_street_name(self):
        """Test parsing address with letter in street name."""
        address = "E. Jacqmainlaan 135, 1000 Brussel"
        result = VATValidationService._parse_address(address)
        self.assertEqual(result, {
            "street_name": "E. Jacqmainlaan",
            "house_number": "135",
            "postal_code": "1000",
            "city": "Brussel"
        })

    def test_malformed_address(self):
        """Test parsing malformed address."""
        address = "Invalid Address Format"
        result = VATValidationService._parse_address(address)
        self.assertEqual(result, {
            "street_name": "Invalid Address Format",
            "house_number": "",
            "postal_code": "",
            "city": ""
        })