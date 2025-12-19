"""
Workflows Services - Business logic for workflow operations
"""
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from .models import (
    WorkflowDefinition, WorkflowState, WorkflowInstance,
    WorkflowHistory, ApprovalRequest, WorkflowNotification
)


class WorkflowError(Exception):
    """Custom exception for workflow errors."""
    pass


def get_or_create_workflow_instance(entity, workflow_definition=None):
    """
    Get or create a workflow instance for an entity.

    Args:
        entity: The model instance (Campaign, MediaPlan, etc.)
        workflow_definition: Optional specific workflow to use

    Returns:
        WorkflowInstance
    """
    content_type = ContentType.objects.get_for_model(entity)

    # Try to get existing instance
    try:
        return WorkflowInstance.objects.get(
            content_type=content_type,
            object_id=entity.id,
            is_active=True
        )
    except WorkflowInstance.DoesNotExist:
        pass

    # Get workflow definition if not provided
    if not workflow_definition:
        entity_type = content_type.model
        workflow_definition = WorkflowDefinition.objects.filter(
            entity_type=entity_type,
            is_active=True,
            is_default=True
        ).first()

        if not workflow_definition:
            raise WorkflowError(
                f'No default workflow found for entity type: {entity_type}'
            )

    # Get initial state
    initial_state = workflow_definition.states.filter(state_type='initial').first()
    if not initial_state:
        raise WorkflowError(
            f'No initial state defined for workflow: {workflow_definition.name}'
        )

    # Create instance
    return WorkflowInstance.objects.create(
        workflow=workflow_definition,
        current_state=initial_state,
        content_type=content_type,
        object_id=entity.id
    )


def get_available_transitions(workflow_instance, user=None):
    """
    Get available transitions for a workflow instance.

    Args:
        workflow_instance: WorkflowInstance
        user: Optional user to filter by permissions

    Returns:
        QuerySet of WorkflowTransition
    """
    return workflow_instance.get_available_transitions(user)


def can_transition(workflow_instance, transition, user=None):
    """
    Check if a transition can be executed.

    Args:
        workflow_instance: WorkflowInstance
        transition: WorkflowTransition
        user: Optional user to check permissions

    Returns:
        tuple (bool, str) - (can_transition, reason)
    """
    # Check transition is from current state
    if transition.from_state != workflow_instance.current_state:
        return False, 'Transition not available from current state'

    # Check user permission
    if user and not user.is_superuser:
        if transition.allowed_groups.exists():
            user_groups = user.groups.all()
            if not transition.allowed_groups.filter(id__in=user_groups).exists():
                return False, 'User does not have permission for this transition'

    # Check if approval is required and pending
    if transition.requires_approval:
        pending_approval = ApprovalRequest.objects.filter(
            workflow_instance=workflow_instance,
            transition=transition,
            status='pending'
        ).exists()

        if pending_approval:
            return False, 'Approval is pending for this transition'

    return True, None


@transaction.atomic
def execute_transition(workflow_instance, transition, user, comment='', metadata=None):
    """
    Execute a workflow transition.

    Args:
        workflow_instance: WorkflowInstance
        transition: WorkflowTransition
        user: User performing the transition
        comment: Optional comment
        metadata: Optional additional metadata

    Returns:
        WorkflowHistory

    Raises:
        WorkflowError: If transition cannot be executed
    """
    can_do, reason = can_transition(workflow_instance, transition, user)
    if not can_do:
        raise WorkflowError(reason)

    # Record history
    history = WorkflowHistory.objects.create(
        instance=workflow_instance,
        transition=transition,
        from_state=workflow_instance.current_state,
        to_state=transition.to_state,
        performed_by=user,
        comment=comment,
        metadata=metadata or {}
    )

    # Update current state
    workflow_instance.current_state = transition.to_state
    workflow_instance.save()

    # Check if final state
    if transition.to_state.state_type == 'final':
        workflow_instance.completed_at = timezone.now()
        workflow_instance.is_active = False
        workflow_instance.save()

    # Update entity status if applicable
    update_entity_status(workflow_instance, transition.to_state)

    return history


def update_entity_status(workflow_instance, new_state):
    """
    Update the entity's status field to match workflow state.

    Args:
        workflow_instance: WorkflowInstance
        new_state: WorkflowState
    """
    entity = workflow_instance.content_object
    if entity and hasattr(entity, 'status'):
        entity.status = new_state.code
        entity.save(update_fields=['status'])


@transaction.atomic
def request_approval(workflow_instance, transition, user, approvers=None, groups=None,
                    min_approvals=1, due_date=None):
    """
    Create an approval request for a transition.

    Args:
        workflow_instance: WorkflowInstance
        transition: WorkflowTransition
        user: User requesting approval
        approvers: List of users who can approve
        groups: List of groups who can approve
        min_approvals: Minimum number of approvals required
        due_date: Optional due date

    Returns:
        ApprovalRequest
    """
    if not transition.requires_approval:
        raise WorkflowError('This transition does not require approval')

    # Check for existing pending request
    existing = ApprovalRequest.objects.filter(
        workflow_instance=workflow_instance,
        transition=transition,
        status='pending'
    ).first()

    if existing:
        return existing

    # Create approval request
    approval_request = ApprovalRequest.objects.create(
        workflow_instance=workflow_instance,
        transition=transition,
        requested_by=user,
        min_approvals=min_approvals,
        due_date=due_date
    )

    if approvers:
        approval_request.required_approvers.set(approvers)
    if groups:
        approval_request.required_groups.set(groups)

    return approval_request


def cancel_approval_request(approval_request, user):
    """Cancel a pending approval request."""
    if approval_request.status != 'pending':
        raise WorkflowError('Only pending approval requests can be cancelled')

    approval_request.status = 'cancelled'
    approval_request.responded_by = user
    approval_request.responded_at = timezone.now()
    approval_request.save()

    return approval_request


def get_pending_approvals(user):
    """
    Get pending approvals for a user.

    Returns approvals where user is in required_approvers or required_groups.
    """
    user_groups = user.groups.all()

    return ApprovalRequest.objects.filter(
        status='pending'
    ).filter(
        models.Q(required_approvers=user) |
        models.Q(required_groups__in=user_groups)
    ).distinct()


def get_user_notifications(user, unread_only=False):
    """Get notifications for a user."""
    queryset = WorkflowNotification.objects.filter(user=user)
    if unread_only:
        queryset = queryset.filter(is_read=False)
    return queryset.order_by('-created_at')


def mark_notification_read(notification):
    """Mark a notification as read."""
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    return notification


def mark_all_notifications_read(user):
    """Mark all notifications for a user as read."""
    WorkflowNotification.objects.filter(
        user=user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
