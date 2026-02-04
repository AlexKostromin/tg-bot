from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.users.views import NotifyAPIView

# Кастомизация заголовков админки
admin.site.site_header = "Панель организатора соревнований"
admin.site.site_title = "Админка бота регистрации"
admin.site.index_title = "Управление пользователями, соревнованиями и заявками"

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API endpoints from apps
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.competitions.urls')),
    path('api/notify/', NotifyAPIView.as_view(), name='notify'),
]
