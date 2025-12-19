"""
Workflows Serializers - Workflow API
"""
from rest_framework import serializers
from .models import (
    WorkflowDefinition, WorkflowState, WorkflowTransition,
    WorkflowInstance, WorkflowHistory,
    ApprovalRequest, ApprovalResponse, WorkflowNotification
)


class WorkflowStateSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowState model."""

    class Meta:
        model = WorkflowState
        fields = [
            'id', 'workflow', 'name', 'code', 'description',
            'state_type', 'color', 'icon', 'display_order',
            'is_editable', 'requires_approval',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkflowTransitionSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowTransition model."""
    from_state_name = serializers.CharField(source='from_state.name', read_only=True)
    to_state_name = serializers.CharField(source='to_state.name', read_only=True)

    class Meta:
        model = WorkflowTransition
        fields = [
            'id', 'workflow', 'name', 'code',
            'from_state', 'from_state_name',
            'to_state', 'to_state_name',
            'allowed_groups', 'requires_comment', 'requires_approval',
            'auto_execute', 'notify_users',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkflowDefinitionSerializer(serializers.ModelSerializer):
    """Full serializer for WorkflowDefinition model."""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    states = WorkflowStateSerializer(many=True, read_only=True)
    transitions = WorkflowTransitionSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowDefinition
        fields = [
            'id', 'tenant', 'tenant_name',
            'name', 'code', 'description',
            'entity_type', 'is_active', 'is_default',
            'states', 'transitions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkflowDefinitionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for WorkflowDefinition list."""
    states_count = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowDefinition
        fields = [
            'id', 'name', 'code', 'entity_type',
            'is_active', 'is_default', 'states_count'
        ]

    def get_states_count(self, obj):
        return obj.states.count()


class WorkflowHistorySerializer(serializers.ModelSerializer):
    """Serializer for WorkflowHistory model."""
    from_state_name = serializers.CharField(source='from_state.name', read_only=True)
    to_state_name = serializers.CharField(source='to_state.name', read_only=True)
    performed_by_name = serializers.CharField(
        source='performed_by.full_name', read_only=True, allow_null=True
    )

    class Meta:
        model = WorkflowHistory
        fields = [
            'id', 'instance', 'transition',
            'from_state', 'from_state_name',
            'to_state', 'to_state_name',
            'performed_by', 'performed_by_name',
            'performed_at', 'comment', 'metadata'
        ]
        read_only_fields = fields


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowInstance model."""
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    current_state_name = serializers.CharField(source='current_state.name', read_only=True)
    current_state_color = serializers.CharField(source='current_state.color', read_only=True)
    available_transitions = serializers.SerializerMethodField()
    history = WorkflowHistorySerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'workflow', 'workflow_name',
            'current_state', 'current_state_name', 'current_state_color',
            'content_type', 'object_id',
            'started_at', 'completed_at', 'is_active',
            'available_transitions', 'history',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields

    def get_available_transitions(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        transitions = obj.get_available_transitions(user)
        return WorkflowTransitionSerializer(transitions, many=True).data


class ApprovalResponseSerializer(serializers.ModelSerializer):
    """Serializer for ApprovalResponse model."""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = ApprovalResponse
        fields = [
            'id', 'approval_request', 'user', 'user_name', 'user_email',
            'is_approved', 'comment', 'responded_at'
        ]
        read_only_fields = ['id', 'responded_at']


class ApprovalRequestSerializer(serializers.ModelSerializer):
    """Serializer for ApprovalRequest model."""
    workflow_instance_info = serializers.SerializerMethodField()
    transition_name = serializers.CharField(source='transition.name', read_only=True)
    requested_by_name = serializers.CharField(
        source='requested_by.full_name', read_only=True, allow_null=True
    )
    responses = ApprovalResponseSerializer(many=True, read_only=True)
    approval_count = serializers.IntegerField(read_only=True)
    rejection_count = serializers.IntegerField(read_only=True)
    is_fully_approved = serializers.BooleanField(read_only=True)

    class Meta:
        model = ApprovalRequest
        fields = [
            'id', 'workflow_instance', 'workflow_instance_info',
            'transition', 'transition_name',
            'status',
            'requested_by', 'requested_by_name', 'requested_at',
            'required_approvers', 'required_groups', 'min_approvals',
            'responded_by', 'responded_at', 'response_comment',
            'due_date',
            'responses', 'approval_count', 'rejection_count', 'is_fully_approved',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'requested_at', 'responded_at',
            'created_at', 'updated_at'
        ]

    def get_workflow_instance_info(self, obj):
        instance = obj.workflow_instance
        return {
            'id': str(instance.id),
            'workflow_name': instance.workflow.name,
            'entity_type': instance.workflow.entity_type,
            'current_state': instance.current_state.name,
        }


class WorkflowNotificationSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowNotification model."""

    class Meta:
        model = WorkflowNotification
        fields = [
            'id', 'user', 'notification_type',
            'workflow_instance', 'approval_request',
            'title', 'message', 'link',
            'is_read', 'read_at',
            'email_sent', 'email_sent_at',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# =============================================================================
# ACTION SERIALIZERS
# =============================================================================

class ExecuteTransitionSerializer(serializers.Serializer):
    """Serializer for executing a transition."""
    transition_id = serializers.UUIDField()
    comment = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)


class RequestApprovalSerializer(serializers.Serializer):
    """Serializer for requesting approval."""
    transition_id = serializers.UUIDField()
    approver_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    min_approvals = serializers.IntegerField(default=1)
    due_date = serializers.DateTimeField(required=False, allow_null=True)


class ApproveRejectSerializer(serializers.Serializer):
    """Serializer for approving or rejecting."""
    is_approved = serializers.BooleanField()
    comment = serializers.CharField(required=False, allow_blank=True)
