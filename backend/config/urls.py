from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.users.views import UserViewSet, NotifyAPIView, RegistrationRequestViewSet
from apps.competitions.views import CompetitionViewSet, VoterTimeSlotViewSet

# Кастомизация заголовков админки
admin.site.site_header = "Панель организатора соревнований"
admin.site.site_title = "Админка бота регистрации"
admin.site.index_title = "Управление пользователями, соревнованиями и заявками"

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'registration-requests', RegistrationRequestViewSet, basename='registration-request')
router.register(r'competitions', CompetitionViewSet, basename='competition')
router.register(r'voter-time-slots', VoterTimeSlotViewSet, basename='voter-time-slot')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/notify/', NotifyAPIView.as_view(), name='notify'),
]
