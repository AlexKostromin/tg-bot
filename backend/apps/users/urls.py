from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegistrationRequestViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'registration-requests', RegistrationRequestViewSet, basename='registration-request')

urlpatterns = router.urls
