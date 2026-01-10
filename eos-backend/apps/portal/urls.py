"""
Portal URLs - Client Portal API Routes
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PortalDashboardView,
    PortalCampaignViewSet, PortalMediaPlanViewSet,
    PortalMessageViewSet, PortalActivityLogViewSet,
    ClientPortalSettingsViewSet
)

router = DefaultRouter()
router.register(r'campaigns', PortalCampaignViewSet, basename='portal-campaign')
router.register(r'media-plans', PortalMediaPlanViewSet, basename='portal-mediaplan')
router.register(r'messages', PortalMessageViewSet, basename='portal-message')
router.register(r'activity', PortalActivityLogViewSet, basename='portal-activity')
router.register(r'settings', ClientPortalSettingsViewSet, basename='portal-settings')

urlpatterns = [
    path('dashboard/', PortalDashboardView.as_view(), name='portal-dashboard'),
    path('', include(router.urls)),
]
