"""
Campaigns Serializers - Module 4 API
"""
from rest_framework import serializers
from .models import (
    Project, Campaign, MediaPlan, Subcampaign,
    SubcampaignVersion, SubcampaignFee, CampaignComment, CampaignDocument
)


# =============================================================================
# PROJECT SERIALIZERS
# =============================================================================

class ProjectSerializer(serializers.ModelSerializer):
    """Full serializer for Project model."""
    advertiser_name = serializers.CharField(source='advertiser.name', read_only=True)
    client_name = serializers.CharField(source='advertiser.client.name', read_only=True)
    agency_name = serializers.CharField(source='advertiser.client.agency.name', read_only=True)
    owner_name = serializers.CharField(source='owner.full_name', read_only=True, allow_null=True)
    planner_name = serializers.CharField(source='planner.full_name', read_only=True, allow_null=True)
    budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    campaigns_count = serializers.SerializerMethodField()
    total_campaign_budget = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'advertiser', 'advertiser_name', 'client_name', 'agency_name',
            'name', 'code', 'description', 'status',
            'start_date', 'end_date',
            'budget_micros', 'budget', 'currency',
            'owner', 'owner_name', 'planner', 'planner_name',
            'notes', 'is_template',
            'campaigns_count', 'total_campaign_budget',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_campaigns_count(self, obj):
        return obj.campaigns.count()

    def get_total_campaign_budget(self, obj):
        return obj.total_campaign_budget_micros / 1_000_000


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Project list."""
    advertiser_name = serializers.CharField(source='advertiser.name', read_only=True)
    client_name = serializers.CharField(source='advertiser.client.name', read_only=True)
    budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    campaigns_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'code', 'status',
            'advertiser_name', 'client_name',
            'start_date', 'end_date',
            'budget', 'currency',
            'campaigns_count',
            'created_at'
        ]

    def get_campaigns_count(self, obj):
        return obj.campaigns.count()


# =============================================================================
# CAMPAIGN SERIALIZERS
# =============================================================================

class CampaignSerializer(serializers.ModelSerializer):
    """Full serializer for Campaign model."""
    project_name = serializers.CharField(source='project.name', read_only=True)
    advertiser_name = serializers.CharField(source='project.advertiser.name', read_only=True)
    owner_name = serializers.CharField(source='owner.full_name', read_only=True, allow_null=True)
    budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    duration_days = serializers.IntegerField(read_only=True)
    media_plans_count = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'project', 'project_name', 'advertiser_name',
            'name', 'code', 'description', 'status', 'objective',
            'start_date', 'end_date', 'duration_days',
            'budget_micros', 'budget', 'currency',
            'target_audience', 'target_countries', 'target_kpis',
            'owner', 'owner_name',
            'notes', 'is_template',
            'media_plans_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_media_plans_count(self, obj):
        return obj.media_plans.count()


class CampaignListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Campaign list."""
    project_name = serializers.CharField(source='project.name', read_only=True)
    budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'code', 'status', 'objective',
            'project_name',
            'start_date', 'end_date',
            'budget', 'currency',
            'created_at'
        ]


# =============================================================================
# MEDIA PLAN SERIALIZERS
# =============================================================================

class MediaPlanSerializer(serializers.ModelSerializer):
    """Full serializer for MediaPlan model."""
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    project_name = serializers.CharField(source='campaign.project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, allow_null=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True, allow_null=True)
    total_budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    subcampaigns_count = serializers.SerializerMethodField()
    allocated_budget = serializers.SerializerMethodField()

    class Meta:
        model = MediaPlan
        fields = [
            'id', 'campaign', 'campaign_name', 'project_name',
            'name', 'version', 'description', 'status',
            'start_date', 'end_date',
            'total_budget_micros', 'total_budget', 'currency',
            'created_by', 'created_by_name',
            'approved_by', 'approved_by_name', 'approved_at',
            'client_approved_by', 'client_approved_at',
            'notes', 'is_active_version',
            'subcampaigns_count', 'allocated_budget',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'version', 'created_at', 'updated_at']

    def get_subcampaigns_count(self, obj):
        return obj.subcampaigns.count()

    def get_allocated_budget(self, obj):
        total = sum(s.budget_micros for s in obj.subcampaigns.all())
        return total / 1_000_000


class MediaPlanListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for MediaPlan list."""
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    total_budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = MediaPlan
        fields = [
            'id', 'name', 'version', 'status',
            'campaign_name',
            'total_budget', 'is_active_version',
            'created_at'
        ]


# =============================================================================
# SUBCAMPAIGN SERIALIZERS
# =============================================================================

class SubcampaignFeeSerializer(serializers.ModelSerializer):
    """Serializer for SubcampaignFee model."""
    calculated_amount = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = SubcampaignFee
        fields = [
            'id', 'subcampaign', 'name', 'fee_type',
            'calculation_method', 'percentage', 'cpm_micros', 'flat_fee_micros',
            'calculated_amount_micros', 'calculated_amount',
            'is_included_in_budget', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'calculated_amount_micros', 'created_at', 'updated_at']


class SubcampaignSerializer(serializers.ModelSerializer):
    """Full serializer for Subcampaign model."""
    media_plan_name = serializers.CharField(source='media_plan.name', read_only=True)
    campaign_name = serializers.CharField(source='media_plan.campaign.name', read_only=True)
    budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    unit_price = serializers.DecimalField(max_digits=18, decimal_places=6, read_only=True)
    fees = SubcampaignFeeSerializer(many=True, read_only=True)
    total_fees = serializers.SerializerMethodField()

    class Meta:
        model = Subcampaign
        fields = [
            'id', 'media_plan', 'media_plan_name', 'campaign_name',
            'name', 'code', 'description', 'status',
            'channel', 'platform',
            'start_date', 'end_date',
            'budget_micros', 'budget', 'currency',
            'buying_type', 'unit_price_micros', 'unit_price', 'estimated_units',
            'target_audience', 'target_locations', 'target_devices',
            'creative_format', 'creative_sizes',
            'external_id', 'external_account_id',
            'notes', 'fees', 'total_fees',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_fees(self, obj):
        total = sum(f.calculated_amount_micros for f in obj.fees.all())
        return total / 1_000_000


class SubcampaignListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Subcampaign list."""
    budget = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = Subcampaign
        fields = [
            'id', 'name', 'code', 'status',
            'channel', 'platform',
            'start_date', 'end_date',
            'budget', 'buying_type',
            'created_at'
        ]


class SubcampaignVersionSerializer(serializers.ModelSerializer):
    """Serializer for SubcampaignVersion model."""
    changed_by_name = serializers.CharField(source='changed_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = SubcampaignVersion
        fields = [
            'id', 'subcampaign', 'version_number',
            'budget_micros', 'start_date', 'end_date', 'status',
            'change_summary', 'changed_by', 'changed_by_name',
            'snapshot_data',
            'created_at'
        ]
        read_only_fields = fields


# =============================================================================
# COMMENT AND DOCUMENT SERIALIZERS
# =============================================================================

class CampaignCommentSerializer(serializers.ModelSerializer):
    """Serializer for CampaignComment model."""
    author_name = serializers.CharField(source='author.full_name', read_only=True, allow_null=True)
    author_email = serializers.CharField(source='author.email', read_only=True, allow_null=True)
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = CampaignComment
        fields = [
            'id', 'campaign', 'author', 'author_name', 'author_email',
            'parent', 'content', 'is_internal',
            'replies_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_replies_count(self, obj):
        return obj.replies.count()

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class CampaignDocumentSerializer(serializers.ModelSerializer):
    """Serializer for CampaignDocument model."""
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True, allow_null=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = CampaignDocument
        fields = [
            'id', 'campaign', 'name', 'document_type',
            'file', 'file_url',
            'uploaded_by', 'uploaded_by_name',
            'is_client_visible', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at', 'updated_at']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


# =============================================================================
# NESTED/DETAIL SERIALIZERS
# =============================================================================

class SubcampaignDetailSerializer(SubcampaignSerializer):
    """Detailed serializer for Subcampaign with versions."""
    versions = SubcampaignVersionSerializer(many=True, read_only=True)

    class Meta(SubcampaignSerializer.Meta):
        fields = SubcampaignSerializer.Meta.fields + ['versions']


class MediaPlanDetailSerializer(MediaPlanSerializer):
    """Detailed serializer for MediaPlan with subcampaigns."""
    subcampaigns = SubcampaignSerializer(many=True, read_only=True)

    class Meta(MediaPlanSerializer.Meta):
        fields = MediaPlanSerializer.Meta.fields + ['subcampaigns']


class CampaignDetailSerializer(CampaignSerializer):
    """Detailed serializer for Campaign with media plans."""
    media_plans = MediaPlanListSerializer(many=True, read_only=True)
    comments = CampaignCommentSerializer(many=True, read_only=True)
    documents = CampaignDocumentSerializer(many=True, read_only=True)

    class Meta(CampaignSerializer.Meta):
        fields = CampaignSerializer.Meta.fields + ['media_plans', 'comments', 'documents']


class ProjectDetailSerializer(ProjectSerializer):
    """Detailed serializer for Project with campaigns."""
    campaigns = CampaignListSerializer(many=True, read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['campaigns']
