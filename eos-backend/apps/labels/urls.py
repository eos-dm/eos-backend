"""
Labels URLs - Taxonomy API Routes
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LabelDefinitionViewSet, LabelLevelViewSet, LabelValueViewSet,
    CampaignLabelViewSet, MediaPlanLabelViewSet,
    SubcampaignLabelViewSet, ProjectLabelViewSet
)

router = DefaultRouter()
router.register(r'definitions', LabelDefinitionViewSet, basename='labeldefinition')
router.register(r'levels', LabelLevelViewSet, basename='labellevel')
router.register(r'values', LabelValueViewSet, basename='labelvalue')
router.register(r'campaign-labels', CampaignLabelViewSet, basename='campaignlabel')
router.register(r'media-plan-labels', MediaPlanLabelViewSet, basename='mediaplanlabel')
router.register(r'subcampaign-labels', SubcampaignLabelViewSet, basename='subcampaignlabel')
router.register(r'project-labels', ProjectLabelViewSet, basename='projectlabel')

urlpatterns = [
    path('', include(router.urls)),
]
