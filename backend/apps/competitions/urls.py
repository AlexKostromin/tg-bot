from rest_framework.routers import DefaultRouter
from .views import CompetitionViewSet, VoterTimeSlotViewSet

router = DefaultRouter()
router.register(r'competitions', CompetitionViewSet, basename='competition')
router.register(r'voter-time-slots', VoterTimeSlotViewSet, basename='voter-time-slot')

urlpatterns = router.urls