from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/vacancies/', include('vacancies.urls')),
    path('api/common/', include('common.urls')),
    path('api/profiles/', include('profiles.urls')),  # Add profiles URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
