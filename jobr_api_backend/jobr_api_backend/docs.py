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
        - Accounts: User management and authentication
        - Profiles: Employee profiles, education, work experience, and portfolio
        - Vacancies: Job listings and applications
        - Chat: Real-time messaging between employers and employees
        - Common: Shared functionality and utilities
        """,
        terms_of_service="https://www.jobr.com/terms/",
        contact=openapi.Contact(email="contact@jobr.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)