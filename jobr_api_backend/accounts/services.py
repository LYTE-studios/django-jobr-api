# services.py
import re
import requests
from functools import wraps
from django.core.cache import cache
from django.core.exceptions import ValidationError
from rest_framework.exceptions import Throttled
from datetime import datetime, timedelta
from typing import Dict, Optional

class VATValidationService:
    VIES_API_URL = "https://ec.europa.eu/taxation_customs/vies/services/checkVatService"
    KBO_API_URL = "https://kbopub.economie.fgov.be/kbopub/zoeknummerform.html"
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
    def _check_rate_limit(cls, ip_address: str) -> None:
        """Check if request is within rate limits."""
        key = f"{cls.RATE_LIMIT_KEY_PREFIX}{ip_address}"
        requests = cache.get(key, 0)
        
        if requests >= cls.MAX_REQUESTS:
            raise Throttled(
                detail="Too many VAT validation requests. Please try again later.",
                wait=cls.RATE_LIMIT_PERIOD
            )
        
        # Increment request count
        cache.set(key, requests + 1, cls.RATE_LIMIT_PERIOD)

    @classmethod
    def _get_cached_result(cls, vat_number: str) -> Optional[Dict]:
        """Get cached validation result."""
        return cache.get(f"{cls.VAT_CACHE_PREFIX}{vat_number}")

    @classmethod
    def _cache_result(cls, vat_number: str, result: Dict) -> None:
        """Cache validation result."""
        cache.set(
            f"{cls.VAT_CACHE_PREFIX}{vat_number}",
            result,
            cls.VAT_CACHE_TIMEOUT
        )

    @classmethod
    def validate_vat(cls, vat_number: str, ip_address: str) -> Dict:
        """
        Validate VAT number and retrieve company details.
        
        Args:
            vat_number: VAT number to validate (format: BE0123456789)
            ip_address: IP address of the requester for rate limiting
            
        Returns:
            Dict containing validation result and company details
            
        Raises:
            ValidationError: If VAT number format is invalid
            Throttled: If rate limit is exceeded
            Exception: For other validation errors
        """
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

        # Check cache
        cached_result = cls._get_cached_result(vat_number)
        if cached_result:
            return cached_result

        try:
            # Call VIES API
            response = requests.post(
                cls.VIES_API_URL,
                json={
                    "countryCode": "BE",
                    "vatNumber": vat_number[2:]  # Remove 'BE' prefix
                }
            )
            
            if response.status_code != 200:
                raise Exception("VIES service unavailable")

            data = response.json()
            
            if not data.get("valid"):
                raise ValidationError({
                    "error": "VAT_NOT_FOUND",
                    "message": "VAT number not found in database"
                })

            # Get additional company details from KBO/BCE
            company_details = cls._get_company_details(vat_number)
            
            result = {
                "is_valid": True,
                "company_details": company_details
            }

            # Cache the result
            cls._cache_result(vat_number, result)
            
            return result

        except requests.RequestException:
            raise Exception({
                "error": "SERVICE_UNAVAILABLE",
                "message": "Unable to validate VAT number at this time"
            })

    @classmethod
    def _get_company_details(cls, vat_number: str) -> Dict:
        """
        Retrieve company details from KBO/BCE database.
        This is a simplified version - in production, you would implement
        actual integration with the KBO/BCE API.
        """
        # Simulate KBO/BCE API call
        # In production, implement actual API integration
        return {
            "name": "Example Company",
            "street_name": "Example Street",
            "house_number": "123",
            "city": "Brussels",
            "postal_code": "1000",
            "country": "Belgium"
        }

class TokenService:
    @staticmethod
    def get_tokens_for_user(user):
        """Generate access and refresh tokens for user"""
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
