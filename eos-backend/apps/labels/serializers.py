"""
Labels Serializers - Taxonomy API
"""
from rest_framework import serializers
from django.conf import settings
from .models import (
    LabelDefinition, LabelLevel, LabelValue,
    CampaignLabel, MediaPlanLabel, SubcampaignLabel, ProjectLabel
)


class LabelLevelSerializer(serializers.ModelSerializer):
    """Serializer for LabelLevel model."""
    values_count = serializers.SerializerMethodField()

    class Meta:
        model = LabelLevel
        fields = [
            'id', 'label_definition', 'name', 'level_number',
            'description', 'is_active', 'values_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_values_count(self, obj):
        return obj.values.count()


class LabelValueSerializer(serializers.ModelSerializer):
    """Serializer for LabelValue model."""
    label_definition_name = serializers.CharField(
        source='label_definition.name', read_only=True
    )
    label_level_name = serializers.CharField(
        source='label_level.name', read_only=True, allow_null=True
    )
    parent_name = serializers.CharField(
        source='parent.name', read_only=True, allow_null=True
    )
    full_path = serializers.CharField(read_only=True)
    depth = serializers.IntegerField(read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = LabelValue
        fields = [
            'id', 'label_definition', 'label_definition_name',
            'label_level', 'label_level_name',
            'parent', 'parent_name',
            'name', 'code', 'description',
            'display_order', 'color', 'icon',
            'is_active', 'external_id', 'metadata',
            'full_path', 'depth', 'children_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_children_count(self, obj):
        return obj.children.count()


class LabelValueNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for LabelValue with children."""
    children = serializers.SerializerMethodField()

    class Meta:
        model = LabelValue
        fields = [
            'id', 'name', 'code', 'display_order', 'color',
            'icon', 'is_active', 'children'
        ]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('display_order', 'name')
        return LabelValueNestedSerializer(children, many=True).data


class LabelDefinitionSerializer(serializers.ModelSerializer):
    """Full serializer for LabelDefinition model."""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    levels = LabelLevelSerializer(many=True, read_only=True)
    values_count = serializers.SerializerMethodField()
    can_add_more = serializers.SerializerMethodField()

    class Meta:
        model = LabelDefinition
        fields = [
            'id', 'tenant', 'tenant_name',
            'name', 'code', 'description',
            'data_type', 'applies_to',
            'display_order', 'is_required', 'is_active',
            'color', 'icon',
            'levels', 'values_count', 'can_add_more',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_values_count(self, obj):
        return obj.values.count()

    def get_can_add_more(self, obj):
        """Check if more label definitions can be added to tenant."""
        max_labels = getattr(settings, 'MAX_LABEL_DEFINITIONS', 20)
        current_count = LabelDefinition.objects.filter(tenant=obj.tenant).count()
        return current_count < max_labels


class LabelDefinitionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for LabelDefinition list."""
    values_count = serializers.SerializerMethodField()

    class Meta:
        model = LabelDefinition
        fields = [
            'id', 'name', 'code', 'data_type', 'applies_to',
            'is_required', 'is_active', 'color', 'values_count'
        ]

    def get_values_count(self, obj):
        return obj.values.count()


class LabelDefinitionDetailSerializer(LabelDefinitionSerializer):
    """Detailed serializer with hierarchical values."""
    values = serializers.SerializerMethodField()

    class Meta(LabelDefinitionSerializer.Meta):
        fields = LabelDefinitionSerializer.Meta.fields + ['values']

    def get_values(self, obj):
        """Get root-level values with nested children."""
        root_values = obj.values.filter(
            parent__isnull=True,
            is_active=True
        ).order_by('display_order', 'name')
        return LabelValueNestedSerializer(root_values, many=True).data


# =============================================================================
# LABEL ASSIGNMENT SERIALIZERS
# =============================================================================

class CampaignLabelSerializer(serializers.ModelSerializer):
    """Serializer for CampaignLabel model."""
    label_value_name = serializers.CharField(source='label_value.name', read_only=True)
    label_value_full_path = serializers.CharField(source='label_value.full_path', read_only=True)
    label_definition_name = serializers.CharField(
        source='label_value.label_definition.name', read_only=True
    )
    assigned_by_name = serializers.CharField(
        source='assigned_by.full_name', read_only=True, allow_null=True
    )

    class Meta:
        model = CampaignLabel
        fields = [
            'id', 'campaign', 'label_value',
            'label_value_name', 'label_value_full_path',
            'label_definition_name',
            'assigned_by', 'assigned_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'assigned_by', 'created_at']

    def create(self, validated_data):
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)


class MediaPlanLabelSerializer(serializers.ModelSerializer):
    """Serializer for MediaPlanLabel model."""
    label_value_name = serializers.CharField(source='label_value.name', read_only=True)
    label_value_full_path = serializers.CharField(source='label_value.full_path', read_only=True)
    label_definition_name = serializers.CharField(
        source='label_value.label_definition.name', read_only=True
    )

    class Meta:
        model = MediaPlanLabel
        fields = [
            'id', 'media_plan', 'label_value',
            'label_value_name', 'label_value_full_path',
            'label_definition_name',
            'assigned_by', 'created_at'
        ]
        read_only_fields = ['id', 'assigned_by', 'created_at']

    def create(self, validated_data):
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)


class SubcampaignLabelSerializer(serializers.ModelSerializer):
    """Serializer for SubcampaignLabel model."""
    label_value_name = serializers.CharField(source='label_value.name', read_only=True)
    label_value_full_path = serializers.CharField(source='label_value.full_path', read_only=True)
    label_definition_name = serializers.CharField(
        source='label_value.label_definition.name', read_only=True
    )

    class Meta:
        model = SubcampaignLabel
        fields = [
            'id', 'subcampaign', 'label_value',
            'label_value_name', 'label_value_full_path',
            'label_definition_name',
            'assigned_by', 'created_at'
        ]
        read_only_fields = ['id', 'assigned_by', 'created_at']

    def create(self, validated_data):
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)


class ProjectLabelSerializer(serializers.ModelSerializer):
    """Serializer for ProjectLabel model."""
    label_value_name = serializers.CharField(source='label_value.name', read_only=True)
    label_value_full_path = serializers.CharField(source='label_value.full_path', read_only=True)
    label_definition_name = serializers.CharField(
        source='label_value.label_definition.name', read_only=True
    )

    class Meta:
        model = ProjectLabel
        fields = [
            'id', 'project', 'label_value',
            'label_value_name', 'label_value_full_path',
            'label_definition_name',
            'assigned_by', 'created_at'
        ]
        read_only_fields = ['id', 'assigned_by', 'created_at']

    def create(self, validated_data):
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)


# =============================================================================
# BULK OPERATIONS
# =============================================================================

class BulkLabelAssignmentSerializer(serializers.Serializer):
    """Serializer for bulk label assignment."""
    label_values = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )


class LabelStatisticsSerializer(serializers.Serializer):
    """Serializer for label statistics response."""
    total_definitions = serializers.IntegerField()
    max_definitions = serializers.IntegerField()
    remaining_slots = serializers.IntegerField()
    total_values = serializers.IntegerField()
    total_assignments = serializers.IntegerField()
    by_entity_type = serializers.DictField()
