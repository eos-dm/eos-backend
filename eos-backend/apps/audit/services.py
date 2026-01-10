"""
Audit Services - Centralized audit logging functions.

These services should be called from the domain/service layer
to ensure all activities are properly logged regardless of entry point
(UI, API, batch processes, scripts).
"""
from typing import Optional, Any, Dict
from uuid import UUID
from django.contrib.auth import get_user_model
from .models import AuditLog, BudgetChangeLog, AuditActionEnum, EntityTypeEnum

User = get_user_model()


def log_audit_event(
    entity_type: str,
    entity_id: UUID,
    action: str,
    description: str,
    user: Optional[User] = None,
    old_state: Optional[str] = None,
    new_state: Optional[str] = None,
    extra_data: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditLog:
    """
    Log an audit event.

    Args:
        entity_type: Type of entity (from EntityTypeEnum)
        entity_id: UUID of the affected entity
        action: Action performed (from AuditActionEnum)
        description: Human-readable description
        user: User who performed the action (None for system actions)
        old_state: Previous state (for state changes)
        new_state: New state (for state changes)
        extra_data: Additional context data
        ip_address: IP address of the request
        user_agent: User agent string

    Returns:
        Created AuditLog instance
    """
    return AuditLog.objects.create(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        description=description,
        created_by=user,
        old_state=old_state,
        new_state=new_state,
        extra_data=extra_data,
        ip_address=ip_address,
        user_agent=user_agent
    )


def log_state_change(
    entity_type: str,
    entity_id: UUID,
    old_state: str,
    new_state: str,
    user: Optional[User] = None,
    reason: Optional[str] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Log a state change event.

    Args:
        entity_type: Type of entity
        entity_id: UUID of the entity
        old_state: Previous state
        new_state: New state
        user: User who made the change
        reason: Optional reason for the change
        ip_address: IP address of the request

    Returns:
        Created AuditLog instance
    """
    description = f"status: {old_state} -> {new_state}"
    if reason:
        description += f" ({reason})"

    return log_audit_event(
        entity_type=entity_type,
        entity_id=entity_id,
        action=AuditActionEnum.STATE_CHANGED,
        description=description,
        user=user,
        old_state=old_state,
        new_state=new_state,
        ip_address=ip_address
    )


def log_budget_change(
    entity_type: str,
    entity_id: UUID,
    field_name: str,
    new_value_micros: int,
    old_value_micros: Optional[int] = None,
    user: Optional[User] = None,
    reason: Optional[str] = None,
    is_manual_override: bool = False,
    entity_state: Optional[str] = None,
    pricing_model_id: Optional[UUID] = None
) -> BudgetChangeLog:
    """
    Log a budget/financial field change.

    Args:
        entity_type: Type of entity
        entity_id: UUID of the entity
        field_name: Name of the field that changed
        new_value_micros: New value in micros
        old_value_micros: Previous value in micros
        user: User who made the change
        reason: Reason for the change (recommended for manual overrides)
        is_manual_override: Whether this was a manual override
        entity_state: State of the entity at time of change
        pricing_model_id: ID of the pricing model used

    Returns:
        Created BudgetChangeLog instance
    """
    return BudgetChangeLog.objects.create(
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        old_value_micros=old_value_micros,
        new_value_micros=new_value_micros,
        changed_by=user,
        reason=reason,
        is_manual_override=is_manual_override,
        entity_state=entity_state,
        pricing_model_id=pricing_model_id
    )


def log_pricing_override(
    entity_id: UUID,
    field_name: str,
    calculated_value_micros: int,
    override_value_micros: int,
    user: User,
    reason: str,
    entity_state: Optional[str] = None,
    pricing_model_id: Optional[UUID] = None
) -> tuple:
    """
    Log a manual pricing override.

    This creates both an AuditLog and BudgetChangeLog entry.

    Args:
        entity_id: UUID of the subcampaign_version
        field_name: Field that was overridden (e.g., 'unit_price_micros')
        calculated_value_micros: Value that would have been calculated
        override_value_micros: Value that user entered
        user: User who made the override
        reason: Reason for the override
        entity_state: Current state of the entity
        pricing_model_id: ID of the pricing model

    Returns:
        Tuple of (AuditLog, BudgetChangeLog)
    """
    # Log in audit_log
    audit_entry = log_audit_event(
        entity_type=EntityTypeEnum.SUBCAMPAIGN_VERSION,
        entity_id=entity_id,
        action=AuditActionEnum.PRICING_OVERRIDDEN,
        description=f"{field_name} manually overridden: {calculated_value_micros} -> {override_value_micros}",
        user=user,
        extra_data={
            'field_name': field_name,
            'calculated_value_micros': calculated_value_micros,
            'override_value_micros': override_value_micros,
            'reason': reason
        }
    )

    # Log in budget_change_log
    budget_entry = log_budget_change(
        entity_type=EntityTypeEnum.SUBCAMPAIGN_VERSION,
        entity_id=entity_id,
        field_name=field_name,
        old_value_micros=calculated_value_micros,
        new_value_micros=override_value_micros,
        user=user,
        reason=reason,
        is_manual_override=True,
        entity_state=entity_state,
        pricing_model_id=pricing_model_id
    )

    return audit_entry, budget_entry


def log_fee_override(
    entity_id: UUID,
    calculated_fee_value: int,
    override_fee_value: int,
    user: User,
    reason: str,
    entity_state: Optional[str] = None
) -> tuple:
    """
    Log a manual fee override.

    This creates both an AuditLog and BudgetChangeLog entry.

    Args:
        entity_id: UUID of the subcampaign_payment_type
        calculated_fee_value: Fee value that would have been calculated
        override_fee_value: Fee value that user entered
        user: User who made the override
        reason: Reason for the override
        entity_state: Current state

    Returns:
        Tuple of (AuditLog, BudgetChangeLog)
    """
    audit_entry = log_audit_event(
        entity_type=EntityTypeEnum.SUBCAMPAIGN_PAYMENT_TYPE,
        entity_id=entity_id,
        action=AuditActionEnum.FEE_OVERRIDDEN,
        description=f"fee_value manually overridden: {calculated_fee_value} -> {override_fee_value}",
        user=user,
        extra_data={
            'calculated_fee_value': calculated_fee_value,
            'override_fee_value': override_fee_value,
            'reason': reason
        }
    )

    budget_entry = log_budget_change(
        entity_type=EntityTypeEnum.SUBCAMPAIGN_PAYMENT_TYPE,
        entity_id=entity_id,
        field_name='fee_value',
        old_value_micros=calculated_fee_value,
        new_value_micros=override_fee_value,
        user=user,
        reason=reason,
        is_manual_override=True,
        entity_state=entity_state
    )

    return audit_entry, budget_entry
