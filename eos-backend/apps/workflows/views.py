"""
Workflows Views - Workflow API Endpoints
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import (
    WorkflowDefinition, WorkflowState, WorkflowTransition,
    WorkflowInstance, WorkflowHistory,
    ApprovalRequest, ApprovalResponse, WorkflowNotification
)
from .serializers import (
    WorkflowDefinitionSerializer, WorkflowDefinitionListSerializer,
    WorkflowStateSerializer, WorkflowTransitionSerializer,
    WorkflowInstanceSerializer, WorkflowHistorySerializer,
    ApprovalRequestSerializer, ApprovalResponseSerializer,
    WorkflowNotificationSerializer,
    ExecuteTransitionSerializer, RequestApprovalSerializer, ApproveRejectSerializer
)
from .services import (
    get_or_create_workflow_instance, execute_transition,
    request_approval, can_transition, WorkflowError,
    get_user_notifications, mark_notification_read, mark_all_notifications_read
)


class WorkflowDefinitionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing workflow definitions.
    """
    queryset = WorkflowDefinition.objects.select_related('tenant').prefetch_related(
        'states', 'transitions'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['entity_type', 'name']
    filterset_fields = ['tenant', 'entity_type', 'is_active', 'is_default']

    def get_serializer_class(self):
        if self.action == 'list':
            return WorkflowDefinitionListSerializer
        return WorkflowDefinitionSerializer

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this workflow as default for its entity type."""
        workflow = self.get_object()

        # Unset other defaults for same entity type and tenant
        WorkflowDefinition.objects.filter(
            tenant=workflow.tenant,
            entity_type=workflow.entity_type,
            is_default=True
        ).update(is_default=False)

        workflow.is_default = True
        workflow.save()

        serializer = self.get_serializer(workflow)
        return Response(serializer.data)


class WorkflowStateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing workflow states.
    """
    queryset = WorkflowState.objects.select_related('workflow').all()
    serializer_class = WorkflowStateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['display_order']
    ordering = ['display_order']
    filterset_fields = ['workflow', 'state_type']


class WorkflowTransitionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing workflow transitions.
    """
    queryset = WorkflowTransition.objects.select_related(
        'workflow', 'from_state', 'to_state'
    ).all()
    serializer_class = WorkflowTransitionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['workflow', 'from_state', 'to_state', 'requires_approval']


class WorkflowInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing workflow instances.
    """
    queryset = WorkflowInstance.objects.select_related(
        'workflow', 'current_state'
    ).prefetch_related('history').all()
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering = ['-created_at']
    filterset_fields = ['workflow', 'current_state', 'is_active', 'content_type']

    @action(detail=True, methods=['post'])
    def execute_transition(self, request, pk=None):
        """Execute a transition for this workflow instance."""
        instance = self.get_object()

        serializer = ExecuteTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transition_id = serializer.validated_data['transition_id']
        comment = serializer.validated_data.get('comment', '')
        metadata = serializer.validated_data.get('metadata', {})

        try:
            transition = WorkflowTransition.objects.get(id=transition_id)
            history = execute_transition(
                instance, transition, request.user,
                comment=comment, metadata=metadata
            )
            return Response({
                'success': True,
                'history': WorkflowHistorySerializer(history).data,
                'instance': WorkflowInstanceSerializer(
                    instance, context={'request': request}
                ).data
            })
        except WorkflowTransition.DoesNotExist:
            return Response(
                {'error': 'Transition not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except WorkflowError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def request_approval(self, request, pk=None):
        """Request approval for a transition."""
        instance = self.get_object()

        serializer = RequestApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transition_id = serializer.validated_data['transition_id']

        try:
            transition = WorkflowTransition.objects.get(id=transition_id)

            from apps.accounts.models import User
            from django.contrib.auth.models import Group

            approvers = None
            groups = None

            if 'approver_ids' in serializer.validated_data:
                approvers = User.objects.filter(
                    id__in=serializer.validated_data['approver_ids']
                )
            if 'group_ids' in serializer.validated_data:
                groups = Group.objects.filter(
                    id__in=serializer.validated_data['group_ids']
                )

            approval = request_approval(
                instance, transition, request.user,
                approvers=approvers,
                groups=groups,
                min_approvals=serializer.validated_data.get('min_approvals', 1),
                due_date=serializer.validated_data.get('due_date')
            )

            return Response(
                ApprovalRequestSerializer(approval).data,
                status=status.HTTP_201_CREATED
            )
        except WorkflowTransition.DoesNotExist:
            return Response(
                {'error': 'Transition not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except WorkflowError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get full history for this workflow instance."""
        instance = self.get_object()
        history = instance.history.all()
        serializer = WorkflowHistorySerializer(history, many=True)
        return Response(serializer.data)


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing approval requests.
    """
    queryset = ApprovalRequest.objects.select_related(
        'workflow_instance', 'transition', 'requested_by', 'responded_by'
    ).prefetch_related('responses', 'required_approvers', 'required_groups').all()
    serializer_class = ApprovalRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering = ['-created_at']
    filterset_fields = ['workflow_instance', 'status', 'requested_by']

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending approvals for current user."""
        user = request.user
        user_groups = user.groups.all()

        pending = self.queryset.filter(
            status='pending'
        ).filter(
            models.Q(required_approvers=user) |
            models.Q(required_groups__in=user_groups)
        ).distinct()

        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Respond to an approval request (approve/reject)."""
        approval_request = self.get_object()

        if approval_request.status != 'pending':
            return Response(
                {'error': 'This approval request is no longer pending'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ApproveRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if user can respond
        user = request.user
        user_groups = user.groups.all()

        can_respond = (
            approval_request.required_approvers.filter(id=user.id).exists() or
            approval_request.required_groups.filter(id__in=user_groups).exists() or
            user.is_superuser
        )

        if not can_respond:
            return Response(
                {'error': 'You are not authorized to respond to this request'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already responded
        if ApprovalResponse.objects.filter(
            approval_request=approval_request, user=user
        ).exists():
            return Response(
                {'error': 'You have already responded to this request'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create response
        response = ApprovalResponse.objects.create(
            approval_request=approval_request,
            user=user,
            is_approved=serializer.validated_data['is_approved'],
            comment=serializer.validated_data.get('comment', '')
        )

        # If rejected, update approval request status
        if not response.is_approved:
            approval_request.status = 'rejected'
            approval_request.responded_by = user
            approval_request.responded_at = timezone.now()
            approval_request.response_comment = response.comment
            approval_request.save()

        return Response(ApprovalResponseSerializer(response).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an approval request."""
        approval_request = self.get_object()

        if approval_request.status != 'pending':
            return Response(
                {'error': 'Only pending requests can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Only requester or admin can cancel
        if approval_request.requested_by != request.user and not request.user.is_superuser:
            return Response(
                {'error': 'Only the requester can cancel this request'},
                status=status.HTTP_403_FORBIDDEN
            )

        approval_request.status = 'cancelled'
        approval_request.responded_by = request.user
        approval_request.responded_at = timezone.now()
        approval_request.save()

        serializer = self.get_serializer(approval_request)
        return Response(serializer.data)


class WorkflowNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing workflow notifications.
    """
    queryset = WorkflowNotification.objects.select_related(
        'user', 'workflow_instance', 'approval_request'
    ).all()
    serializer_class = WorkflowNotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering = ['-created_at']
    filterset_fields = ['notification_type', 'is_read']

    def get_queryset(self):
        """Filter to only show current user's notifications."""
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications."""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        mark_notification_read(notification)
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        mark_all_notifications_read(request.user)
        return Response({'success': True})


# Import models for queryset filters
from django.db import models
