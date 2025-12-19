"""
Workflows Signals - Handle workflow events
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    WorkflowHistory, ApprovalRequest, ApprovalResponse,
    WorkflowNotification
)


@receiver(post_save, sender=WorkflowHistory)
def on_workflow_state_change(sender, instance, created, **kwargs):
    """Handle workflow state changes."""
    if not created:
        return

    workflow_instance = instance.instance

    # Create notification for state change
    if instance.performed_by:
        WorkflowNotification.objects.create(
            user=instance.performed_by,
            notification_type='state_changed',
            workflow_instance=workflow_instance,
            title=f'State changed to {instance.to_state.name}',
            message=f'The status has been changed from {instance.from_state.name} to {instance.to_state.name}.',
        )


@receiver(post_save, sender=ApprovalRequest)
def on_approval_request_created(sender, instance, created, **kwargs):
    """Notify approvers when approval is requested."""
    if not created:
        return

    # Notify required approvers
    for user in instance.required_approvers.all():
        WorkflowNotification.objects.create(
            user=user,
            notification_type='approval_required',
            workflow_instance=instance.workflow_instance,
            approval_request=instance,
            title='Approval Required',
            message=f'Your approval is required for a {instance.workflow_instance.workflow.entity_type}.',
        )


@receiver(post_save, sender=ApprovalResponse)
def on_approval_response(sender, instance, created, **kwargs):
    """Handle approval responses."""
    if not created:
        return

    approval_request = instance.approval_request

    # Check if fully approved
    if approval_request.is_fully_approved and approval_request.status == 'pending':
        approval_request.status = 'approved'
        approval_request.responded_by = instance.user
        approval_request.responded_at = timezone.now()
        approval_request.save()

        # Execute the transition
        workflow_instance = approval_request.workflow_instance
        transition = approval_request.transition

        from .services import execute_transition
        execute_transition(
            workflow_instance,
            transition,
            instance.user,
            comment=f'Auto-approved after {approval_request.approval_count} approvals'
        )

    # Notify requester
    if approval_request.requested_by:
        notification_type = 'approval_received' if instance.is_approved else 'rejection_received'
        action = 'approved' if instance.is_approved else 'rejected'

        WorkflowNotification.objects.create(
            user=approval_request.requested_by,
            notification_type=notification_type,
            workflow_instance=approval_request.workflow_instance,
            approval_request=approval_request,
            title=f'Approval {action}',
            message=f'{instance.user.full_name} has {action} your request.',
        )
