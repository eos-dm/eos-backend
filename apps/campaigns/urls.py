"""
Campaigns URLs - Module 4 API Routes
Based on EOS Schema V100
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProjectViewSet, MediaPlanViewSet, CampaignViewSet,
    SubcampaignViewSet, SubcampaignVersionViewSet
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'media-plans', MediaPlanViewSet, basename='mediaplan')
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'subcampaigns', SubcampaignViewSet, basename='subcampaign')
router.register(r'subcampaign-versions', SubcampaignVersionViewSet, basename='subcampaignversion')

urlpatterns = [
    path('', include(router.urls)),
]
