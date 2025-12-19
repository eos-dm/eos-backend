"""
Workflows URLs - Workflow API Routes
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    WorkflowDefinitionViewSet, WorkflowStateViewSet, WorkflowTransitionViewSet,
    WorkflowInstanceViewSet, ApprovalRequestViewSet, WorkflowNotificationViewSet
)

router = DefaultRouter()
router.register(r'definitions', WorkflowDefinitionViewSet, basename='workflowdefinition')
router.register(r'states', WorkflowStateViewSet, basename='workflowstate')
router.register(r'transitions', WorkflowTransitionViewSet, basename='workflowtransition')
router.register(r'instances', WorkflowInstanceViewSet, basename='workflowinstance')
router.register(r'approvals', ApprovalRequestViewSet, basename='approvalrequest')
router.register(r'notifications', WorkflowNotificationViewSet, basename='workflownotification')

urlpatterns = [
    path('', include(router.urls)),
]
