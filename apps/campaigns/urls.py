"""
Campaigns URLs - Module 4 API Routes
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProjectViewSet, CampaignViewSet, MediaPlanViewSet,
    SubcampaignViewSet, SubcampaignFeeViewSet,
    CampaignCommentViewSet, CampaignDocumentViewSet
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'media-plans', MediaPlanViewSet, basename='mediaplan')
router.register(r'subcampaigns', SubcampaignViewSet, basename='subcampaign')
router.register(r'subcampaign-fees', SubcampaignFeeViewSet, basename='subcampaignfee')
router.register(r'comments', CampaignCommentViewSet, basename='campaigncomment')
router.register(r'documents', CampaignDocumentViewSet, basename='campaigndocument')

urlpatterns = [
    path('', include(router.urls)),
]
