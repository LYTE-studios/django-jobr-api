# services.py
import re
import requests
from functools import wraps
from django.core.cache import cache
from rest_framework.exceptions import ValidationError, Throttled
from datetime import datetime, timedelta
from typing import Dict, Optional
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .models import VATValidationResult

class VATValidationService:
    API_URL = "https://api.vatcheckapi.com/v1/validate"
    VAT_CACHE_PREFIX = "vat_validation_"
    VAT_CACHE_TIMEOUT = 86400  # 24 hours in seconds
    RATE_LIMIT_KEY_PREFIX = "vat_validation_ratelimit_"
    MAX_REQUESTS = 100  # Maximum requests per hour
    RATE_LIMIT_PERIOD = 3600  # 1 hour in seconds

    @classmethod
    def _validate_be_vat_format(cls, vat_number: str) -> bool:
        """Validate Belgian VAT number format."""
        pattern = r'^BE[0-9]{10}$'
        return bool(re.match(pattern, vat_number.upper()))

    @classmethod
    def _parse_address(cls, address: str) -> Dict[str, str]:
        """
        Parse Belgian address string into components.
        Handles various formats including:
        - Standard: "Rijselsestraat 8, 8500 Kortrijk"
        - With bus: "Nieuwstraat 12 bus 3, 2000 Antwerpen"
        - With house number suffix: "Avenue Louise 123A, 1050 Ixelles"
        - With range: "Brusselsestraat 10-12, 2800 Mechelen"
        - Without house number: "Grote Markt, 1000 Brussel"
        - Multi-word street/city: "Prins van Luiklaan 24, 1070 Anderlecht"
        """
        # Initialize default values
        result = {
            "street_name": "",
            "house_number": "",
            "postal_code": "",
            "city": ""
        }

        # Clean the input
        address = address.strip()
        if not address:
            return result

        # Split into street part and postal/city part (handle both comma and newline)
        parts = address.replace('\n', ',').split(',', 1)
        street_part = parts[0].strip()
        postal_city_part = parts[1].strip() if len(parts) > 1 else ""

        # First try to match the postal code and city from the second part
        if postal_city_part:
            postal_city_match = re.match(r'^(\d{4})\s+(.+)$', postal_city_part)
            if postal_city_match:
                result["postal_code"] = postal_city_match.group(1).strip()
                result["city"] = postal_city_match.group(2).strip()

        # Now handle the street part with various patterns
        # Try to match house number at the end of street_part
        patterns = [
            # Match "Street 123 bus 4"
            r'^(.*?)\s+(\d+(?:[A-Za-z])?(?:\s+bus\s+\d+)?)\s*$',
            # Match "Street 123-125"
            r'^(.*?)\s+(\d+(?:[-/]\d+)?)\s*$',
            # Match "Street 123A"
            r'^(.*?)\s+(\d+[A-Za-z]?)\s*$',
            # Match just "Street 123"
            r'^(.*?)\s+(\d+)\s*$'
        ]

        for pattern in patterns:
            street_match = re.match(pattern, street_part)
            if street_match:
                result["street_name"] = street_match.group(1).strip()
                result["house_number"] = street_match.group(2).strip()
                break
        else:
            # If no pattern matches, assume it's all street name
            result["street_name"] = street_part.strip()

        return result

    @classmethod
    def _check_rate_limit(cls, ip_address: str) -> None:
        """Check if request is within rate limits."""
        if not ip_address:
            return  # Skip rate limiting if no IP address provided
            
        key = f"{cls.RATE_LIMIT_KEY_PREFIX}{ip_address}"
        requests = cache.get(key) or 0  # Ensure we get an integer, not None
        
        if requests >= cls.MAX_REQUESTS:
            raise Throttled(
                detail="Too many VAT validation requests. Please try again later.",
                wait=cls.RATE_LIMIT_PERIOD
            )
        
        # Increment request count
        cache.set(key, requests + 1, timeout=cls.RATE_LIMIT_PERIOD)

    @classmethod
    def _get_cached_result(cls, vat_number: str) -> Optional[Dict]:
        """Get cached validation result."""
        return cache.get(f"{cls.VAT_CACHE_PREFIX}{vat_number}")

    @classmethod
    def _cache_result(cls, vat_number: str, result: Dict) -> None:
        """Cache validation result."""
        cache.set(f"{cls.VAT_CACHE_PREFIX}{vat_number}", result, timeout=cls.VAT_CACHE_TIMEOUT)

    @classmethod
    def validate_vat(cls, vat_number: str, ip_address: str, employer = None) -> Dict:
        """
        Validate VAT number and retrieve company details using vatcheckapi.com.
        
        Args:
            vat_number: VAT number to validate (format: BE0123456789)
            ip_address: IP address of the requester for rate limiting
            employer: Optional employer instance to link the validation result to
            
        Returns:
            Dict containing validation result and company details
            
        Raises:
            ValidationError: If VAT number format is invalid
            Throttled: If rate limit is exceeded
            Exception: For other validation errors
        """
        # Check API key configuration
        if not getattr(settings, 'VATCHECKAPI_KEY', None):
            raise ValidationError({
                "error": "SERVICE_UNAVAILABLE",
                "message": "VAT validation service is not properly configured"
            })

        # Check rate limit
        cls._check_rate_limit(ip_address)

        # Normalize VAT number
        vat_number = vat_number.upper().strip()

        # Check format
        if not cls._validate_be_vat_format(vat_number):
            raise ValidationError({
                "error": "INVALID_FORMAT",
                "message": "Invalid VAT number format. Must start with BE followed by 10 digits"
            })

        # Check database first
        try:
            validation_result = VATValidationResult.objects.get(vat_number=vat_number)
            # If employer exists and is linked to this validation, use their details
            if validation_result.company:
                employer = validation_result.company
                return {
                    "is_valid": validation_result.is_valid,
                    "company_details": {
                        "name": employer.name,
                        "street_name": employer.street_name,
                        "house_number": employer.house_number,
                        "city": employer.city,
                        "postal_code": employer.postal_code,
                        "country": "Belgium"
                    }
                }
            else:
                # Fall back to parsing stored address if no employer is linked
                address_parts = cls._parse_address(validation_result.company_address)
                return {
                    "is_valid": validation_result.is_valid,
                    "company_details": {
                        "name": validation_result.company_name,
                        "street_name": address_parts["street_name"],
                        "house_number": address_parts["house_number"],
                        "city": address_parts["city"],
                        "postal_code": address_parts["postal_code"],
                        "country": "Belgium"
                    }
                }
        except VATValidationResult.DoesNotExist:
            pass

        # Check cache
        cached_result = cls._get_cached_result(vat_number)
        if cached_result:
            return cached_result

        try:
            # Call vatcheckapi.com API
            response = requests.get(
                f"{cls.API_URL}/{vat_number}",
                headers={
                    "apikey": settings.VATCHECKAPI_KEY
                }
            )

            if response.status_code == 404:
                # Store invalid result in database
                VATValidationResult.objects.create(
                    vat_number=vat_number,
                    is_valid=False,
                    employer=employer
                )
                raise ValidationError({
                    "error": "VAT_NOT_FOUND",
                    "message": "VAT number not found"
                })
            
            if response.status_code != 200:
                raise ValidationError({
                    "error": "SERVICE_UNAVAILABLE",
                    "message": "VAT validation service is currently unavailable"
                })

            data = response.json()
            
            if not data.get("valid"):
                # Store invalid result in database
                VATValidationResult.objects.create(
                    vat_number=vat_number,
                    is_valid=False,
                    employer=employer
                )
                raise ValidationError({
                    "error": "VAT_NOT_FOUND",
                    "message": "VAT number is not valid"
                })

            # Parse the address from the API response
            address_parts = cls._parse_address(data.get("address", ""))

            # Store valid result in database and update employer details
            validation_result = VATValidationResult.objects.create(
                vat_number=vat_number,
                is_valid=True,
                company_name=data.get("name", ""),
                company_address=data.get("address", ""),
                employer=employer
            )

            # Update employer details if provided
            if employer:
                employer.company_name = data.get("name", "")
                employer.street_name = address_parts["street_name"]
                employer.house_number = address_parts["house_number"]
                employer.city = address_parts["city"]
                employer.postal_code = address_parts["postal_code"]
                employer.save()

            # Format the response according to requirements
            result = {
                "is_valid": True,
                "company_details": {
                    "name": data.get("name", ""),
                    "street_name": address_parts["street_name"],
                    "house_number": address_parts["house_number"],
                    "city": address_parts["city"],
                    "postal_code": address_parts["postal_code"],
                    "country": "Belgium"
                }
            }

            # Cache the result
            cls._cache_result(vat_number, result)
            
            return result

        except requests.RequestException as e:
            raise ValidationError({
                "error": "SERVICE_UNAVAILABLE",
                "message": f"Unable to validate VAT number: {str(e)}"
            })

class CompanyService:
    @staticmethod
    def get_first_company_vat_number(user):
        """
        Get the VAT number of the first company created by a user.
        Args:
            user: CustomUser instance
        Returns:
            str or None: VAT number if found, None otherwise
        """
        if user.role != 'employer':
            return None
            
        first_company = user.companies.order_by('created_at').first()
        return first_company.vat_number if first_company else None

class TokenService:
    @staticmethod
    def get_tokens_for_user(user):
        """Generate access and refresh tokens for user"""
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
