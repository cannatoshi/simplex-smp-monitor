"""URL patterns für Clients API"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SimplexClientViewSet, ClientConnectionViewSet, ClientStatsView, TestMessageViewSet, TestRunViewSet

router = DefaultRouter()
router.register(r'clients', SimplexClientViewSet, basename='client')
router.register(r'connections', ClientConnectionViewSet, basename='connection')
router.register(r'messages', TestMessageViewSet, basename='message')
router.register(r'test-runs', TestRunViewSet, basename='testrun')

urlpatterns = [
    path('', include(router.urls)),
    path('clients-stats/', ClientStatsView.as_view(), name='client-stats'),
]
