from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from .docs import schema_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/vacancies/', include('vacancies.urls')),
    path('api/common/', include('common.urls')),
    path('api/profiles/', include('profiles.urls')),
    
    # API Documentation
    path('', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # Root shows ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # Media files
    path('api/media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Global API settings
API_TITLE = 'Jobr API'
API_DESCRIPTION = 'API for the Jobr platform'
API_VERSION = 'v1'
API_TERMS_OF_SERVICE = 'https://www.jobr.com/terms/'
API_CONTACT_EMAIL = 'contact@jobr.com'
API_LICENSE_NAME = 'BSD License'
