"""
Workflows Admin - Workflow Administration
"""
from django.contrib import admin
from .models import (
    WorkflowDefinition, WorkflowState, WorkflowTransition,
    WorkflowInstance, WorkflowHistory,
    ApprovalRequest, ApprovalResponse, WorkflowNotification
)


class WorkflowStateInline(admin.TabularInline):
    model = WorkflowState
    extra = 1
    ordering = ['display_order']


class WorkflowTransitionInline(admin.TabularInline):
    model = WorkflowTransition
    extra = 1
    fk_name = 'workflow'


@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'tenant', 'entity_type', 'is_active', 'is_default']
    list_filter = ['tenant', 'entity_type', 'is_active', 'is_default']
    search_fields = ['name', 'code', 'description']
    inlines = [WorkflowStateInline, WorkflowTransitionInline]

    fieldsets = (
        (None, {
            'fields': ('tenant', 'name', 'code', 'description')
        }),
        ('Configuration', {
            'fields': ('entity_type', 'is_active', 'is_default')
        }),
    )


@admin.register(WorkflowState)
class WorkflowStateAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'workflow', 'state_type', 'display_order', 'is_editable']
    list_filter = ['workflow', 'state_type', 'is_editable', 'requires_approval']
    search_fields = ['name', 'code']
    ordering = ['workflow', 'display_order']


@admin.register(WorkflowTransition)
class WorkflowTransitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'workflow', 'from_state', 'to_state', 'requires_approval']
    list_filter = ['workflow', 'requires_approval', 'auto_execute']
    search_fields = ['name', 'code']
    filter_horizontal = ['allowed_groups']


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'current_state', 'content_type', 'object_id', 'is_active', 'started_at']
    list_filter = ['workflow', 'current_state', 'is_active', 'content_type']
    readonly_fields = ['content_type', 'object_id', 'started_at', 'completed_at']


@admin.register(WorkflowHistory)
class WorkflowHistoryAdmin(admin.ModelAdmin):
    list_display = ['instance', 'from_state', 'to_state', 'performed_by', 'performed_at']
    list_filter = ['instance__workflow', 'performed_at']
    readonly_fields = ['instance', 'transition', 'from_state', 'to_state', 'performed_by', 'performed_at']


class ApprovalResponseInline(admin.TabularInline):
    model = ApprovalResponse
    extra = 0
    readonly_fields = ['user', 'is_approved', 'comment', 'responded_at']


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ['workflow_instance', 'transition', 'status', 'requested_by', 'requested_at', 'due_date']
    list_filter = ['status', 'requested_at']
    search_fields = ['workflow_instance__workflow__name']
    readonly_fields = ['requested_at', 'responded_at']
    filter_horizontal = ['required_approvers', 'required_groups']
    inlines = [ApprovalResponseInline]


@admin.register(ApprovalResponse)
class ApprovalResponseAdmin(admin.ModelAdmin):
    list_display = ['approval_request', 'user', 'is_approved', 'responded_at']
    list_filter = ['is_approved', 'responded_at']
    readonly_fields = ['responded_at']


@admin.register(WorkflowNotification)
class WorkflowNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'email_sent']
    search_fields = ['title', 'message', 'user__email']
