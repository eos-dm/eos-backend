"""
Portal Serializers - Client Portal API
"""
from rest_framework import serializers
from .models import (
    ClientPortalSettings, PortalMessage, PortalMessageAttachment, PortalActivityLog
)
from apps.campaigns.models import Campaign, MediaPlan, Project
from apps.campaigns.serializers import CampaignListSerializer, MediaPlanListSerializer


class ClientPortalSettingsSerializer(serializers.ModelSerializer):
    """Serializer for ClientPortalSettings model."""
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = ClientPortalSettings
        fields = [
            'id', 'client', 'client_name',
            'can_view_campaigns', 'can_view_media_plans',
            'can_view_budgets', 'can_view_reports',
            'can_download_reports', 'can_approve', 'can_comment',
            'welcome_message', 'custom_logo', 'primary_color',
            'email_on_new_campaign', 'email_on_approval_request',
            'email_on_status_change',
            'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PortalMessageAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for PortalMessageAttachment model."""
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PortalMessageAttachment
        fields = ['id', 'message', 'name', 'file', 'file_url', 'file_size', 'mime_type']
        read_only_fields = ['id', 'file_size', 'mime_type']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class PortalMessageSerializer(serializers.ModelSerializer):
    """Serializer for PortalMessage model."""
    sender_name = serializers.CharField(source='sender.full_name', read_only=True, allow_null=True)
    sender_email = serializers.CharField(source='sender.email', read_only=True, allow_null=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True, allow_null=True)
    attachments = PortalMessageAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = PortalMessage
        fields = [
            'id', 'client', 'campaign', 'campaign_name',
            'sender', 'sender_name', 'sender_email',
            'subject', 'content',
            'is_read', 'read_by', 'read_at',
            'has_attachments', 'attachments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sender', 'is_read', 'read_by', 'read_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class PortalMessageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for PortalMessage list."""
    sender_name = serializers.CharField(source='sender.full_name', read_only=True, allow_null=True)

    class Meta:
        model = PortalMessage
        fields = [
            'id', 'subject', 'sender_name', 'is_read',
            'has_attachments', 'created_at'
        ]


class PortalActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for PortalActivityLog model."""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = PortalActivityLog
        fields = [
            'id', 'user', 'user_email', 'user_name', 'client',
            'action', 'entity_type', 'entity_id', 'entity_name',
            'ip_address', 'metadata',
            'created_at'
        ]
        read_only_fields = fields


# =============================================================================
# PORTAL-SPECIFIC DATA SERIALIZERS
# =============================================================================

class PortalDashboardSerializer(serializers.Serializer):
    """Serializer for portal dashboard data."""
    welcome_message = serializers.CharField()
    active_campaigns = serializers.IntegerField()
    pending_approvals = serializers.IntegerField()
    recent_campaigns = CampaignListSerializer(many=True)
    pending_media_plans = MediaPlanListSerializer(many=True)
    unread_messages = serializers.IntegerField()


class PortalCampaignSerializer(serializers.ModelSerializer):
    """Serializer for campaigns in portal view."""
    project_name = serializers.CharField(source='project.name', read_only=True)
    advertiser_name = serializers.CharField(source='project.advertiser.name', read_only=True)
    media_plans_count = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'code', 'status', 'objective',
            'project_name', 'advertiser_name',
            'start_date', 'end_date',
            'media_plans_count',
            'created_at'
        ]

    def get_media_plans_count(self, obj):
        return obj.media_plans.count()


class PortalMediaPlanSerializer(serializers.ModelSerializer):
    """Serializer for media plans in portal view."""
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    subcampaigns_summary = serializers.SerializerMethodField()

    class Meta:
        model = MediaPlan
        fields = [
            'id', 'name', 'version', 'status',
            'campaign_name',
            'start_date', 'end_date',
            'total_budget_micros',
            'subcampaigns_summary',
            'created_at'
        ]

    def get_subcampaigns_summary(self, obj):
        """Get summary of subcampaigns by channel."""
        summary = {}
        for sc in obj.subcampaigns.all():
            if sc.channel not in summary:
                summary[sc.channel] = {
                    'count': 0,
                    'budget_micros': 0
                }
            summary[sc.channel]['count'] += 1
            summary[sc.channel]['budget_micros'] += sc.budget_micros
        return summary


class PortalApprovalSerializer(serializers.Serializer):
    """Serializer for approval action in portal."""
    is_approved = serializers.BooleanField()
    comment = serializers.CharField(required=False, allow_blank=True)
