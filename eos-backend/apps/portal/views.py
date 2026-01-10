"""
Portal Views - Client Portal API Endpoints
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q

from apps.core.permissions import IsClientPortalUser
from apps.campaigns.models import Campaign, MediaPlan, Project
from apps.accounts.models import ClientMembership

from .models import (
    ClientPortalSettings, PortalMessage, PortalMessageAttachment, PortalActivityLog
)
from .serializers import (
    ClientPortalSettingsSerializer,
    PortalMessageSerializer, PortalMessageListSerializer,
    PortalMessageAttachmentSerializer, PortalActivityLogSerializer,
    PortalDashboardSerializer, PortalCampaignSerializer, PortalMediaPlanSerializer,
    PortalApprovalSerializer
)


class PortalPermissionMixin:
    """Mixin to filter data based on client portal access."""

    def get_client_ids(self):
        """Get client IDs the user has access to."""
        user = self.request.user
        if user.is_superuser:
            return None  # Access to all
        return list(
            ClientMembership.objects.filter(user=user).values_list('client_id', flat=True)
        )


class PortalDashboardView(APIView, PortalPermissionMixin):
    """
    Portal Dashboard - Main dashboard for client portal.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        client_ids = self.get_client_ids()

        # Get settings
        settings_obj = None
        welcome_message = "Welcome to the Client Portal"

        if client_ids:
            settings_obj = ClientPortalSettings.objects.filter(
                client_id__in=client_ids
            ).first()
            if settings_obj:
                welcome_message = settings_obj.welcome_message or welcome_message

        # Get campaigns
        campaigns_query = Campaign.objects.select_related('project', 'project__advertiser')
        if client_ids:
            campaigns_query = campaigns_query.filter(
                project__advertiser__client_id__in=client_ids
            )

        active_campaigns = campaigns_query.filter(status='active').count()
        recent_campaigns = campaigns_query.order_by('-created_at')[:5]

        # Get pending media plans for approval
        pending_plans = MediaPlan.objects.filter(
            status='pending_client_review'
        )
        if client_ids:
            pending_plans = pending_plans.filter(
                campaign__project__advertiser__client_id__in=client_ids
            )

        # Get unread messages
        unread_messages = 0
        if client_ids:
            unread_messages = PortalMessage.objects.filter(
                client_id__in=client_ids,
                is_read=False
            ).count()

        # Log activity
        if client_ids:
            PortalActivityLog.objects.create(
                user=user,
                client_id=client_ids[0] if client_ids else None,
                action='login',
                ip_address=self._get_client_ip(request)
            )

        data = {
            'welcome_message': welcome_message,
            'active_campaigns': active_campaigns,
            'pending_approvals': pending_plans.count(),
            'recent_campaigns': PortalCampaignSerializer(recent_campaigns, many=True).data,
            'pending_media_plans': PortalMediaPlanSerializer(pending_plans, many=True).data,
            'unread_messages': unread_messages
        }

        return Response(data)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class PortalCampaignViewSet(viewsets.ReadOnlyModelViewSet, PortalPermissionMixin):
    """
    Portal Campaigns - Campaign listing for client portal.
    """
    queryset = Campaign.objects.select_related(
        'project', 'project__advertiser', 'project__advertiser__client'
    ).all()
    serializer_class = PortalCampaignSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'start_date', 'created_at']
    ordering = ['-created_at']
    filterset_fields = ['status', 'objective']

    def get_queryset(self):
        queryset = super().get_queryset()
        client_ids = self.get_client_ids()
        if client_ids:
            queryset = queryset.filter(
                project__advertiser__client_id__in=client_ids
            )
        # Only show relevant statuses to clients
        return queryset.exclude(status__in=['draft', 'cancelled'])


class PortalMediaPlanViewSet(viewsets.ReadOnlyModelViewSet, PortalPermissionMixin):
    """
    Portal Media Plans - Media plan listing for client portal.
    """
    queryset = MediaPlan.objects.select_related(
        'campaign', 'campaign__project', 'campaign__project__advertiser'
    ).prefetch_related('subcampaigns').all()
    serializer_class = PortalMediaPlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering = ['-created_at']
    filterset_fields = ['status', 'campaign']

    def get_queryset(self):
        queryset = super().get_queryset()
        client_ids = self.get_client_ids()
        if client_ids:
            queryset = queryset.filter(
                campaign__project__advertiser__client_id__in=client_ids
            )
        # Only show client-relevant statuses
        return queryset.filter(
            status__in=['pending_client_review', 'client_approved', 'active', 'completed']
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve or reject a media plan."""
        media_plan = self.get_object()

        if media_plan.status != 'pending_client_review':
            return Response(
                {'error': 'Media plan is not pending review'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PortalApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_approved = serializer.validated_data['is_approved']
        comment = serializer.validated_data.get('comment', '')

        if is_approved:
            media_plan.status = 'client_approved'
            media_plan.client_approved_by = request.user
            media_plan.client_approved_at = timezone.now()
        else:
            media_plan.status = 'internal_approved'  # Send back for revision
            # TODO: Create rejection comment/notification

        media_plan.save()

        # Log activity
        client_ids = self.get_client_ids()
        if client_ids:
            PortalActivityLog.objects.create(
                user=request.user,
                client_id=client_ids[0],
                action='approve' if is_approved else 'reject',
                entity_type='media_plan',
                entity_id=media_plan.id,
                entity_name=media_plan.name,
                metadata={'comment': comment}
            )

        return Response({
            'success': True,
            'status': media_plan.status,
            'message': 'Media plan approved' if is_approved else 'Media plan sent back for revision'
        })


class PortalMessageViewSet(viewsets.ModelViewSet, PortalPermissionMixin):
    """
    Portal Messages - Messaging for client portal.
    """
    queryset = PortalMessage.objects.select_related(
        'sender', 'campaign'
    ).prefetch_related('attachments').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering = ['-created_at']
    filterset_fields = ['is_read', 'campaign']

    def get_serializer_class(self):
        if self.action == 'list':
            return PortalMessageListSerializer
        return PortalMessageSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        client_ids = self.get_client_ids()
        if client_ids:
            queryset = queryset.filter(client_id__in=client_ids)
        return queryset

    def perform_create(self, serializer):
        client_ids = self.get_client_ids()
        if not client_ids:
            raise serializers.ValidationError('No client access')

        serializer.save(
            sender=self.request.user,
            client_id=client_ids[0]
        )

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a message as read."""
        message = self.get_object()

        if not message.is_read:
            message.is_read = True
            message.read_by = request.user
            message.read_at = timezone.now()
            message.save()

        serializer = self.get_serializer(message)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all messages as read."""
        client_ids = self.get_client_ids()
        if client_ids:
            PortalMessage.objects.filter(
                client_id__in=client_ids,
                is_read=False
            ).update(
                is_read=True,
                read_by=request.user,
                read_at=timezone.now()
            )
        return Response({'success': True})


class PortalActivityLogViewSet(viewsets.ReadOnlyModelViewSet, PortalPermissionMixin):
    """
    Portal Activity Log - Activity log for client portal (admin only).
    """
    queryset = PortalActivityLog.objects.select_related('user', 'client').all()
    serializer_class = PortalActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering = ['-created_at']
    filterset_fields = ['action', 'user', 'client']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Regular users can only see their own activity
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        client_ids = self.get_client_ids()
        if client_ids:
            queryset = queryset.filter(client_id__in=client_ids)

        return queryset


class ClientPortalSettingsViewSet(viewsets.ModelViewSet, PortalPermissionMixin):
    """
    Portal Settings - Settings management for client portal.
    """
    queryset = ClientPortalSettings.objects.select_related('client').all()
    serializer_class = ClientPortalSettingsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client', 'is_active']

    def get_queryset(self):
        queryset = super().get_queryset()
        client_ids = self.get_client_ids()
        if client_ids:
            queryset = queryset.filter(client_id__in=client_ids)
        return queryset


# Import serializers for use in views
from rest_framework import serializers
