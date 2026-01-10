"""
Workflows Models - State Machine and Approval System

This module provides workflow management using django-river for state machines
and custom approval tracking.
"""
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
import uuid


class WorkflowDefinition(BaseModel):
    """
    Workflow Definition - Defines a workflow template.
    """
    ENTITY_TYPE_CHOICES = [
        ('campaign', _('Campaign')),
        ('media_plan', _('Media Plan')),
        ('subcampaign', _('Subcampaign')),
        ('project', _('Project')),
    ]

    tenant = models.ForeignKey(
        'core.Tenant',
        on_delete=models.CASCADE,
        related_name='workflow_definitions',
        verbose_name=_('tenant')
    )

    name = models.CharField(_('name'), max_length=255)
    code = models.CharField(_('code'), max_length=50)
    description = models.TextField(_('description'), blank=True)

    entity_type = models.CharField(
        _('entity type'),
        max_length=20,
        choices=ENTITY_TYPE_CHOICES
    )

    is_active = models.BooleanField(_('is active'), default=True)
    is_default = models.BooleanField(_('is default'), default=False)

    class Meta:
        verbose_name = _('workflow definition')
        verbose_name_plural = _('workflow definitions')
        ordering = ['entity_type', 'name']
        unique_together = [['tenant', 'code']]

    def __str__(self):
        return f"{self.name} ({self.entity_type})"


class WorkflowState(BaseModel):
    """
    Workflow State - Defines possible states in a workflow.
    """
    STATE_TYPE_CHOICES = [
        ('initial', _('Initial')),
        ('intermediate', _('Intermediate')),
        ('final', _('Final')),
    ]

    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name='states',
        verbose_name=_('workflow')
    )

    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=50)
    description = models.TextField(_('description'), blank=True)

    state_type = models.CharField(
        _('state type'),
        max_length=20,
        choices=STATE_TYPE_CHOICES,
        default='intermediate'
    )

    # Display
    color = models.CharField(_('color'), max_length=7, default='#6B7280')
    icon = models.CharField(_('icon'), max_length=50, blank=True)
    display_order = models.PositiveIntegerField(_('display order'), default=0)

    # Behavior
    is_editable = models.BooleanField(
        _('is editable'),
        default=True,
        help_text=_('Can entity be edited in this state?')
    )
    requires_approval = models.BooleanField(
        _('requires approval'),
        default=False
    )

    class Meta:
        verbose_name = _('workflow state')
        verbose_name_plural = _('workflow states')
        ordering = ['workflow', 'display_order']
        unique_together = [['workflow', 'code']]

    def __str__(self):
        return f"{self.workflow.name} - {self.name}"


class WorkflowTransition(BaseModel):
    """
    Workflow Transition - Defines allowed transitions between states.
    """
    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name='transitions',
        verbose_name=_('workflow')
    )

    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=50)

    from_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.CASCADE,
        related_name='outgoing_transitions',
        verbose_name=_('from state')
    )
    to_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.CASCADE,
        related_name='incoming_transitions',
        verbose_name=_('to state')
    )

    # Permissions
    allowed_groups = models.ManyToManyField(
        'auth.Group',
        related_name='allowed_transitions',
        verbose_name=_('allowed groups'),
        blank=True
    )

    # Behavior
    requires_comment = models.BooleanField(_('requires comment'), default=False)
    requires_approval = models.BooleanField(_('requires approval'), default=False)
    auto_execute = models.BooleanField(
        _('auto execute'),
        default=False,
        help_text=_('Execute automatically when conditions are met')
    )

    # Notifications
    notify_users = models.BooleanField(_('notify users'), default=True)

    class Meta:
        verbose_name = _('workflow transition')
        verbose_name_plural = _('workflow transitions')
        ordering = ['workflow', 'from_state__display_order']
        unique_together = [['workflow', 'from_state', 'to_state']]

    def __str__(self):
        return f"{self.from_state.name} → {self.to_state.name}"


class WorkflowInstance(BaseModel):
    """
    Workflow Instance - Tracks workflow state for a specific entity.
    """
    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name='instances',
        verbose_name=_('workflow')
    )
    current_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.PROTECT,
        related_name='current_instances',
        verbose_name=_('current state')
    )

    # Generic relation to the entity
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Metadata
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('workflow instance')
        verbose_name_plural = _('workflow instances')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.workflow.name} - {self.current_state.name}"

    def get_available_transitions(self, user=None):
        """Get transitions available from current state."""
        transitions = self.workflow.transitions.filter(from_state=self.current_state)

        if user and not user.is_superuser:
            # Filter by user's groups
            user_groups = user.groups.all()
            transitions = transitions.filter(
                models.Q(allowed_groups__isnull=True) |
                models.Q(allowed_groups__in=user_groups)
            ).distinct()

        return transitions


class WorkflowHistory(BaseModel):
    """
    Workflow History - Tracks state changes.
    """
    instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('instance')
    )
    transition = models.ForeignKey(
        WorkflowTransition,
        on_delete=models.SET_NULL,
        related_name='history',
        verbose_name=_('transition'),
        null=True
    )

    from_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.PROTECT,
        related_name='history_from',
        verbose_name=_('from state')
    )
    to_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.PROTECT,
        related_name='history_to',
        verbose_name=_('to state')
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='workflow_actions',
        verbose_name=_('performed by'),
        null=True
    )
    performed_at = models.DateTimeField(_('performed at'), auto_now_add=True)

    comment = models.TextField(_('comment'), blank=True)

    # Additional context
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)

    class Meta:
        verbose_name = _('workflow history')
        verbose_name_plural = _('workflow histories')
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.from_state.name} → {self.to_state.name} by {self.performed_by}"


# =============================================================================
# APPROVAL SYSTEM
# =============================================================================

class ApprovalRequest(BaseModel):
    """
    Approval Request - Tracks approval requirements and responses.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    ]

    workflow_instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='approval_requests',
        verbose_name=_('workflow instance')
    )
    transition = models.ForeignKey(
        WorkflowTransition,
        on_delete=models.CASCADE,
        related_name='approval_requests',
        verbose_name=_('transition')
    )

    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Requested by
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='requested_approvals',
        verbose_name=_('requested by'),
        null=True
    )
    requested_at = models.DateTimeField(_('requested at'), auto_now_add=True)

    # Approval details
    required_approvers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='required_approvals',
        verbose_name=_('required approvers'),
        blank=True
    )
    required_groups = models.ManyToManyField(
        'auth.Group',
        related_name='required_approvals',
        verbose_name=_('required groups'),
        blank=True
    )
    min_approvals = models.PositiveSmallIntegerField(
        _('minimum approvals'),
        default=1
    )

    # Response
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='responded_approvals',
        verbose_name=_('responded by'),
        null=True,
        blank=True
    )
    responded_at = models.DateTimeField(_('responded at'), null=True, blank=True)
    response_comment = models.TextField(_('response comment'), blank=True)

    # Deadlines
    due_date = models.DateTimeField(_('due date'), null=True, blank=True)

    class Meta:
        verbose_name = _('approval request')
        verbose_name_plural = _('approval requests')
        ordering = ['-created_at']

    def __str__(self):
        return f"Approval for {self.workflow_instance} - {self.status}"

    @property
    def approval_count(self):
        return self.responses.filter(is_approved=True).count()

    @property
    def rejection_count(self):
        return self.responses.filter(is_approved=False).count()

    @property
    def is_fully_approved(self):
        return self.approval_count >= self.min_approvals


class ApprovalResponse(BaseModel):
    """
    Approval Response - Individual approval/rejection from a user.
    """
    approval_request = models.ForeignKey(
        ApprovalRequest,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name=_('approval request')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='approval_responses',
        verbose_name=_('user')
    )

    is_approved = models.BooleanField(_('is approved'))
    comment = models.TextField(_('comment'), blank=True)
    responded_at = models.DateTimeField(_('responded at'), auto_now_add=True)

    class Meta:
        verbose_name = _('approval response')
        verbose_name_plural = _('approval responses')
        unique_together = [['approval_request', 'user']]
        ordering = ['-responded_at']

    def __str__(self):
        action = 'approved' if self.is_approved else 'rejected'
        return f"{self.user} {action}"


# =============================================================================
# NOTIFICATIONS
# =============================================================================

class WorkflowNotification(BaseModel):
    """
    Workflow Notification - Notifications related to workflow events.
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('state_changed', _('State Changed')),
        ('approval_required', _('Approval Required')),
        ('approval_received', _('Approval Received')),
        ('rejection_received', _('Rejection Received')),
        ('deadline_approaching', _('Deadline Approaching')),
        ('deadline_passed', _('Deadline Passed')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workflow_notifications',
        verbose_name=_('user')
    )

    notification_type = models.CharField(
        _('notification type'),
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES
    )

    # Related objects
    workflow_instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('workflow instance'),
        null=True,
        blank=True
    )
    approval_request = models.ForeignKey(
        ApprovalRequest,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('approval request'),
        null=True,
        blank=True
    )

    # Content
    title = models.CharField(_('title'), max_length=255)
    message = models.TextField(_('message'))
    link = models.CharField(_('link'), max_length=500, blank=True)

    # Status
    is_read = models.BooleanField(_('is read'), default=False)
    read_at = models.DateTimeField(_('read at'), null=True, blank=True)

    # Delivery
    email_sent = models.BooleanField(_('email sent'), default=False)
    email_sent_at = models.DateTimeField(_('email sent at'), null=True, blank=True)

    class Meta:
        verbose_name = _('workflow notification')
        verbose_name_plural = _('workflow notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user}"
