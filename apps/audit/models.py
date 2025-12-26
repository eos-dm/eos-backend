"""
Audit Models - Audit Log and Budget Change Log
Based on EOS Schema V100 Documentation

This module implements comprehensive auditing for:
- All state changes and events (audit_log)
- All financial/budget changes (budget_change_log)

Key Design Principles:
- ALL activities affecting planning entities must be logged
- Auditing happens at service/domain layer, not UI
- Includes changes from API, batch processes, and scripts
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class AuditActionEnum(models.TextChoices):
    """Actions that can be logged in audit_log"""
    CREATED = 'created', _('Created')
    UPDATED = 'updated', _('Updated')
    DELETED = 'deleted', _('Deleted')
    STATE_CHANGED = 'state_changed', _('State Changed')
    APPROVED = 'approved', _('Approved')
    REJECTED = 'rejected', _('Rejected')
    RETURNED = 'returned', _('Returned')
    PRICING_OVERRIDDEN = 'pricing_overridden', _('Pricing Overridden')
    FEE_OVERRIDDEN = 'fee_overridden', _('Fee Overridden')
    PERM_CHANGED = 'perm_changed', _('Permission Changed')
    BUDGET_HOLD_CREATED = 'budget_hold_created', _('Budget Hold Created')
    BUDGET_HOLD_CLOSED = 'budget_hold_closed', _('Budget Hold Closed')
    MONTH_CLOSURE_CREATED = 'month_closure_created', _('Month Closure Created')
    MONTH_CLOSURE_CLOSED = 'month_closure_closed', _('Month Closure Closed')
    MONTH_CLOSURE_REOPENED = 'month_closure_reopened', _('Month Closure Reopened')


class EntityTypeEnum(models.TextChoices):
    """Entity types that can be audited"""
    SUBCAMPAIGN = 'subcampaign', _('Subcampaign')
    SUBCAMPAIGN_VERSION = 'subcampaign_version', _('Subcampaign Version')
    SUBCAMPAIGN_PAYMENT_TYPE = 'subcampaign_payment_type', _('Subcampaign Payment Type')
    CREATIVE_ASSIGNMENT = 'creative_assignment', _('Creative Assignment')
    CREATIVE_APPROVAL = 'creative_approval', _('Creative Approval')
    BUDGET_HOLD = 'budget_hold', _('Budget Hold')
    MONTH_CLOSURE = 'month_closure', _('Month Closure')
    APPROVAL_REQUEST = 'approval_request', _('Approval Request')
    APPROVAL_STEP_INSTANCE = 'approval_step_instance', _('Approval Step Instance')
    APPROVAL_ACTION = 'approval_action', _('Approval Action')
    PRICING_ADJUSTMENT_RULE = 'pricing_adjustment_rule', _('Pricing Adjustment Rule')
    PERFORMANCE_PRICING_MODEL = 'performance_pricing_model', _('Performance Pricing Model')
    PROJECT = 'project', _('Project')
    MEDIA_PLAN = 'media_plan', _('Media Plan')
    CAMPAIGN = 'campaign', _('Campaign')
    CLIENT = 'client', _('Client')
    ADVERTISER = 'advertiser', _('Advertiser')
    COST_CENTER = 'cost_center', _('Cost Center')


# =============================================================================
# AUDIT LOG
# =============================================================================

class AuditLog(models.Model):
    """
    Audit Log - Records ALL events/activities in the system.

    Usage:
    - State changes (DRAFT -> LIVE, etc.)
    - CRUD operations on critical entities
    - Approval workflow actions
    - Pricing/fee overrides
    - Permission changes

    All auditable actions MUST be registered here.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What entity was affected
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        choices=EntityTypeEnum.choices
    )
    entity_id = models.UUIDField(
        _('entity ID'),
        help_text=_('UUID of the affected entity')
    )

    # What action was performed
    action = models.CharField(
        _('action'),
        max_length=30,
        choices=AuditActionEnum.choices
    )

    # Description of the change
    description = models.TextField(
        _('description'),
        help_text=_('Human-readable description of the change')
    )

    # For state changes, capture old and new state
    old_state = models.CharField(
        _('old state'),
        max_length=50,
        blank=True,
        null=True
    )
    new_state = models.CharField(
        _('new state'),
        max_length=50,
        blank=True,
        null=True
    )

    # Additional context as JSON
    extra_data = models.JSONField(
        _('extra data'),
        blank=True,
        null=True,
        help_text=_('Additional context data in JSON format')
    )

    # Who made the change
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='audit_audit_logs',
        verbose_name=_('created by'),
        null=True,
        blank=True,
        help_text=_('User who performed the action (null for system actions)')
    )

    # When
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    # IP address for security tracking
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        blank=True,
        null=True
    )

    # User agent for tracking source
    user_agent = models.CharField(
        _('user agent'),
        max_length=500,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('audit log')
        verbose_name_plural = _('audit logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['action']),
            models.Index(fields=['created_by']),
            models.Index(fields=['created_at']),
            models.Index(fields=['entity_type', 'action']),
        ]

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id} - {self.action} at {self.created_at}"


# =============================================================================
# BUDGET CHANGE LOG
# =============================================================================

class BudgetChangeLog(models.Model):
    """
    Budget Change Log - Records ALL changes to financial/budget fields.

    Tracks changes to:
    - subcampaign_version.unit_price_micros
    - subcampaign_version.planned_budget_micros
    - subcampaign_version.planned_units
    - subcampaign_payment_type.fee_value
    - Any other monetary field in micros

    Every manual override of pricing, budget, or fee MUST have an entry here.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What entity was affected
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        choices=EntityTypeEnum.choices
    )
    entity_id = models.UUIDField(
        _('entity ID'),
        help_text=_('UUID of the affected entity')
    )

    # Which field was changed
    field_name = models.CharField(
        _('field name'),
        max_length=100,
        help_text=_('Name of the field that was changed (e.g., planned_budget_micros)')
    )

    # Old and new values
    old_value_micros = models.BigIntegerField(
        _('old value (micros)'),
        null=True,
        blank=True,
        help_text=_('Previous value (null if field was empty)')
    )
    new_value_micros = models.BigIntegerField(
        _('new value (micros)'),
        help_text=_('New value after the change')
    )

    # Reason for the change (strongly recommended for manual overrides)
    reason = models.TextField(
        _('reason'),
        blank=True,
        null=True,
        help_text=_('Reason for the change (required for manual overrides)')
    )

    # Was this a manual override?
    is_manual_override = models.BooleanField(
        _('is manual override'),
        default=False,
        help_text=_('True if this was a manual override by user')
    )

    # Who made the change
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='budget_changes',
        verbose_name=_('changed by'),
        null=True,
        blank=True
    )

    # When
    changed_at = models.DateTimeField(_('changed at'), auto_now_add=True)

    # Context: what was the state of the entity when this change was made?
    entity_state = models.CharField(
        _('entity state'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('State of the entity at the time of change')
    )

    # Reference to pricing model used (for traceability)
    pricing_model_id = models.UUIDField(
        _('pricing model ID'),
        blank=True,
        null=True,
        help_text=_('ID of the pricing model used for calculation')
    )

    class Meta:
        verbose_name = _('budget change log')
        verbose_name_plural = _('budget change logs')
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['field_name']),
            models.Index(fields=['changed_by']),
            models.Index(fields=['changed_at']),
            models.Index(fields=['is_manual_override']),
        ]

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id}.{self.field_name} changed at {self.changed_at}"

    @property
    def old_value(self):
        """Returns old value as decimal (divides by 1M)"""
        if self.old_value_micros is not None:
            return self.old_value_micros / 1_000_000
        return None

    @property
    def new_value(self):
        """Returns new value as decimal (divides by 1M)"""
        return self.new_value_micros / 1_000_000

    @property
    def change_delta_micros(self):
        """Returns the difference between new and old values"""
        if self.old_value_micros is not None:
            return self.new_value_micros - self.old_value_micros
        return self.new_value_micros

    @property
    def change_delta(self):
        """Returns the difference as decimal"""
        return self.change_delta_micros / 1_000_000
