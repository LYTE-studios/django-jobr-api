from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Jobr API",
        default_version='v1',
        description="""
        Jobr Platform API Documentation

        # Overview
        The Jobr API provides endpoints for managing job listings, user profiles, and communications between employers and employees.

        # Authentication
        Most endpoints require JWT authentication. Include the JWT token in the Authorization header:
        `Authorization: Bearer <your_token>`

        # Modules
        - Accounts: User management, authentication, and business validation services
          * VAT Number Validation:
            - Endpoint: POST /api/accounts/validate-vat/
            - Rate limit: 100 requests per hour
            - Caching: Results cached for 24 hours
            - Authentication required
            - Request format:
              ```json
              {
                  "vat_number": "BE0123456789"
              }
              ```
            - Success response:
              ```json
              {
                  "is_valid": true,
                  "company_details": {
                      "name": "Company Name",
                      "street_name": "Street Name",
                      "house_number": "123",
                      "city": "City Name",
                      "postal_code": "1000",
                      "country": "Belgium"
                  }
              }
              ```
            - Error responses:
              * Invalid format:
                ```json
                {
                    "error": "INVALID_FORMAT",
                    "message": "Invalid VAT number format. Must start with BE followed by 10 digits"
                }
                ```
              * VAT not found:
                ```json
                {
                    "error": "VAT_NOT_FOUND",
                    "message": "VAT number not found in database"
                }
                ```
              * Service unavailable:
                ```json
                {
                    "error": "SERVICE_UNAVAILABLE",
                    "message": "Unable to validate VAT number at this time"
                }
                ```
        - Profiles: Employee profiles, education, work experience, and portfolio
        - Vacancies: Job listings and applications
        - Chat: Real-time messaging between employers and employees
        - Common: Shared functionality and utilities

        # WebSocket API
        The Chat module includes WebSocket endpoints for real-time messaging.

        WebSocket URL: `wss://api.jobr.lytestudios.be/ws/chat/{chatroom_id}/`

        Authentication: Include your JWT token in the connection query parameter:
        `wss://api.jobr.lytestudios.be/ws/chat/{chatroom_id}/?token=your_jwt_token`

        Message Types:
        1. Send Message:
        ```json
        {
            "type": "chat.message",
            "data": {
                "content": "Your message here"
            }
        }
        ```

        2. Typing Status:
        ```json
        {
            "type": "chat.typing",
            "data": {
                "is_typing": true
            }
        }
        ```

        3. Read Status:
        ```json
        {
            "type": "chat.read",
            "data": {
                "last_read_message_id": 123
            }
        }
        ```

        Server Responses:
        1. Message Event:
        ```json
        {
            "type": "chat.message",
            "message": {
                "id": 123,
                "content": "Message content",
                "sender_id": 456,
                "timestamp": "2025-03-23T10:24:56+01:00"
            }
        }
        ```

        2. Typing Event:
        ```json
        {
            "type": "chat.typing",
            "user_id": 456,
            "is_typing": true
        }
        ```

        3. Read Event:
        ```json
        {
            "type": "chat.read",
            "user_id": 456,
            "last_read_message_id": 123
        }
        ```

        Error Response:
        ```json
        {
            "error": "Error message here"
        }
        ```

        Note: Only users who are participants in the chatroom (either employer or employee) can connect to the WebSocket.
        """,
        terms_of_service="https://www.jobr.com/terms/",
        contact=openapi.Contact(email="contact@jobr.com"),
        license=openapi.License(name="BSD License"),
    ),
    url="https://api.jobr.lytestudios.be",
    public=True,
    permission_classes=(permissions.AllowAny,),
)