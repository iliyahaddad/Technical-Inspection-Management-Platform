from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from apps.accounts.views import LoginView, LogoutView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('api/auth/token/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/auth/2fa/', include('apps.accounts.two_factor_urls')),
    path('api/auth/logout/', LogoutView.as_view(), name='token_logout'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/health/', include('config.health_urls')),
    path('metrics/', include('config.metrics_urls')),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/clients/', include('apps.clients.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/inspections/', include('apps.inspections.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/mts/', include('apps.mts.urls')),
    path('api/documents/', include('apps.documents.urls')),
    path('api/audit/', include('apps.audit.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
