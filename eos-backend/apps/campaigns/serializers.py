"""
Campaigns Serializers - Module 4 API
Based on EOS Schema V100
"""
from rest_framework import serializers
from .models import (
    Project, MediaPlan, Campaign, Subcampaign, SubcampaignVersion
)


# =============================================================================
# PROJECT SERIALIZERS
# =============================================================================

class ProjectSerializer(serializers.ModelSerializer):
    """Full serializer for Project model."""
    advertiser_name = serializers.CharField(source='advertiser.name', read_only=True)
    client_name = serializers.CharField(source='advertiser.client.name', read_only=True)
    agency_name = serializers.CharField(source='advertiser.client.cost_center.agency.name', read_only=True)
    media_plans_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'advertiser', 'advertiser_name', 'client_name', 'agency_name',
            'name', 'internal_code', 'description', 'status',
            'is_active',
            'media_plans_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_media_plans_count(self, obj):
        return obj.media_plans.count()


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Project list."""
    advertiser_name = serializers.CharField(source='advertiser.name', read_only=True)
    client_name = serializers.CharField(source='advertiser.client.name', read_only=True)
    media_plans_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'internal_code', 'status',
            'advertiser_name', 'client_name',
            'is_active',
            'media_plans_count',
            'created_at'
        ]

    def get_media_plans_count(self, obj):
        return obj.media_plans.count()


# =============================================================================
# MEDIA PLAN SERIALIZERS
# =============================================================================

class MediaPlanSerializer(serializers.ModelSerializer):
    """Full serializer for MediaPlan model."""
    project_name = serializers.CharField(source='project.name', read_only=True)
    total_budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    campaigns_count = serializers.SerializerMethodField()

    class Meta:
        model = MediaPlan
        fields = [
            'id', 'project', 'project_name',
            'name', 'notes', 'external_id', 'status',
            'start_date', 'end_date',
            'total_budget_micros', 'total_budget',
            'is_active',
            'campaigns_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_campaigns_count(self, obj):
        return obj.campaigns.count()


class MediaPlanListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for MediaPlan list."""
    project_name = serializers.CharField(source='project.name', read_only=True)
    total_budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = MediaPlan
        fields = [
            'id', 'name', 'status',
            'project_name',
            'start_date', 'end_date',
            'total_budget', 'is_active',
            'created_at'
        ]


# =============================================================================
# CAMPAIGN SERIALIZERS
# =============================================================================

class CampaignSerializer(serializers.ModelSerializer):
    """Full serializer for Campaign model."""
    media_plan_name = serializers.CharField(source='media_plan.name', read_only=True)
    project_name = serializers.CharField(source='media_plan.project.name', read_only=True)
    total_budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    subcampaigns_count = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'media_plan', 'media_plan_name', 'project_name',
            'campaign_name', 'internal_campaign_name', 'external_id',
            'landing_url',
            'start_date', 'end_date',
            'category', 'product', 'language',
            'total_budget_micros', 'total_budget',
            'invoice_reference',
            'is_active',
            'subcampaigns_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_subcampaigns_count(self, obj):
        return obj.subcampaigns.count()


class CampaignListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Campaign list."""
    media_plan_name = serializers.CharField(source='media_plan.name', read_only=True)
    total_budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id', 'campaign_name', 'internal_campaign_name',
            'media_plan_name',
            'start_date', 'end_date',
            'total_budget', 'is_active',
            'created_at'
        ]


# =============================================================================
# SUBCAMPAIGN SERIALIZERS
# =============================================================================

class SubcampaignSerializer(serializers.ModelSerializer):
    """Full serializer for Subcampaign model."""
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)
    media_plan_name = serializers.CharField(source='campaign.media_plan.name', read_only=True)
    is_editable = serializers.BooleanField(read_only=True)

    class Meta:
        model = Subcampaign
        fields = [
            'id', 'campaign', 'campaign_name', 'media_plan_name',
            'name', 'subcampaign_code', 'objective', 'status',
            'goal', 'publisher', 'tactic', 'creative_type', 'country', 'effort',
            'trafficker_user',
            'l5_custom1', 'l8_custom2', 'l9_custom3', 'l11_custom4', 'l13_custom5',
            'l15_custom6', 'l16_custom7', 'l17_custom8', 'l19_custom9', 'l20_custom10',
            'city_geoname_id',
            'is_active', 'is_editable',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'subcampaign_code', 'created_at', 'updated_at']


class SubcampaignListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Subcampaign list."""
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)
    is_editable = serializers.BooleanField(read_only=True)

    class Meta:
        model = Subcampaign
        fields = [
            'id', 'name', 'subcampaign_code', 'status',
            'campaign_name',
            'goal', 'publisher',
            'is_active', 'is_editable',
            'created_at'
        ]


class SubcampaignVersionSerializer(serializers.ModelSerializer):
    """Serializer for SubcampaignVersion model."""
    unit_price = serializers.DecimalField(max_digits=18, decimal_places=6, read_only=True)
    planned_budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    is_editable = serializers.BooleanField(read_only=True)

    class Meta:
        model = SubcampaignVersion
        fields = [
            'id', 'subcampaign', 'version_number', 'version_name',
            'start_date', 'end_date', 'status',
            'currency', 'media_unit_type', 'performance_pricing_model',
            'unit_price_micros', 'unit_price', 'is_unit_price_overwritten',
            'planned_units', 'planned_budget_micros', 'planned_budget',
            'is_active', 'is_editable',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# =============================================================================
# NESTED/DETAIL SERIALIZERS
# =============================================================================

class SubcampaignDetailSerializer(SubcampaignSerializer):
    """Detailed serializer for Subcampaign with versions."""
    versions = SubcampaignVersionSerializer(many=True, read_only=True)

    class Meta(SubcampaignSerializer.Meta):
        fields = SubcampaignSerializer.Meta.fields + ['versions']


class CampaignDetailSerializer(CampaignSerializer):
    """Detailed serializer for Campaign with subcampaigns."""
    subcampaigns = SubcampaignListSerializer(many=True, read_only=True)

    class Meta(CampaignSerializer.Meta):
        fields = CampaignSerializer.Meta.fields + ['subcampaigns']


class MediaPlanDetailSerializer(MediaPlanSerializer):
    """Detailed serializer for MediaPlan with campaigns."""
    campaigns = CampaignListSerializer(many=True, read_only=True)

    class Meta(MediaPlanSerializer.Meta):
        fields = MediaPlanSerializer.Meta.fields + ['campaigns']


class ProjectDetailSerializer(ProjectSerializer):
    """Detailed serializer for Project with media plans."""
    media_plans = MediaPlanListSerializer(many=True, read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['media_plans']
