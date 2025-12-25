"""
Payments Models - Payment Methods, Pricing Adjustment Rules
Based on EOS Schema V100

This module implements:
- PaymentMethods (defined by cost_center, optional advertiser override)
- SubcampaignPaymentType (fee tracking per subcampaign with date range)
- PricingAdjustmentRule (pricing adjustments with date ranges and override flag)

V100 Changes from V67:
- REMOVED: FeeAdjustmentRule (deleted in V100)
- REMOVED: payment_method_id and media_unit_type_id from SubcampaignPaymentType
- ADDED: is_fee_value_overwritten to SubcampaignPaymentType
- ADDED: updated_at to SubcampaignPaymentType
- CHANGED: fee_type uses utils_type_enum, fee_value_micros renamed to fee_value
- CHANGED: pricing_adjustment_rule - removed media_unit_type_id and payment_method_id
- ADDED: payment_method enum field and is_adjustment_value_micros_overwritten to PricingAdjustmentRule
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel


# =============================================================================
# ENUMS
# =============================================================================

class PaymentTypeEnum(models.TextChoices):
    """Payment type for payment methods"""
    MEDIA_UNIT_TYPE = 'media_unit_type', _('Media Unit Type')
    FEE = 'fee', _('Fee')


class PaymentMethodEnum(models.TextChoices):
    """V100: payment_method_enum - Payment method types"""
    PREPAID = 'PREPAID', _('Prepaid')
    POSTPAID = 'POSTPAID', _('Postpaid')
    CREDIT = 'CREDIT', _('Credit')


class UtilsTypeEnum(models.TextChoices):
    """V100: utils_type_enum - Utility types for fee calculations"""
    PCT = 'PCT', _('Percentage')
    FLAT = 'FLAT', _('Flat Amount')
    ABS = 'ABS', _('Absolute')


class AdjustmentKindEnum(models.TextChoices):
    """V100: adjustment_kind_enum for pricing adjustments"""
    PCT_OF_BASE_MICROS = 'PCT_OF_BASE_MICROS', _('Percentage of Base (Micros)')
    ABS_MICROS = 'ABS_MICROS', _('Absolute (Micros)')
    OVERRIDE_MICROS = 'OVERRIDE_MICROS', _('Override (Micros)')


class PricingAdjustmentTargetKindEnum(models.TextChoices):
    """V100: pricing_adj_target_kind enum"""
    COST_CENTER = 'cost_center', _('Cost Center')
    CLIENT = 'client', _('Client')
    ADVERTISER = 'advertiser', _('Advertiser')


# Legacy enum kept for backwards compatibility during migration
class FeeTypeEnum(models.TextChoices):
    """Legacy fee type enum (use UtilsTypeEnum for new code)"""
    PCT = 'PCT', _('Percentage')
    FLAT = 'FLAT', _('Flat Amount')


# =============================================================================
# PAYMENT METHODS
# =============================================================================

class PaymentMethod(BaseModel):
    """
    Payment Method - Defines payment types at cost_center level with optional advertiser override.
    V100: id uuid [pk], cost_center_id uuid [not null], advertiser_id uuid [null]

    Rules:
    - If payment_type = 'media_unit_type', media_unit_type_id must be NOT NULL
    - If payment_type = 'fee', fee_type and fee_value_micros must be NOT NULL
    """
    cost_center = models.ForeignKey(
        'core.CostCenter',
        on_delete=models.CASCADE,
        related_name='payment_methods',
        verbose_name=_('cost center')
    )
    advertiser = models.ForeignKey(
        'core.Advertiser',
        on_delete=models.CASCADE,
        related_name='payment_method_overrides',
        verbose_name=_('advertiser override'),
        null=True,
        blank=True,
        help_text=_('Optional override for specific advertiser')
    )

    payment_type = models.CharField(
        _('payment type'),
        max_length=20,
        choices=PaymentTypeEnum.choices
    )

    # For payment_type = 'media_unit_type'
    media_unit_type = models.ForeignKey(
        'entities.MediaUnitType',
        on_delete=models.PROTECT,
        related_name='payment_methods',
        verbose_name=_('media unit type'),
        null=True,
        blank=True
    )

    # For payment_type = 'fee'
    fee_type = models.CharField(
        _('fee type'),
        max_length=10,
        choices=FeeTypeEnum.choices,
        null=True,
        blank=True
    )
    fee_value_micros = models.BigIntegerField(
        _('fee value (micros)'),
        null=True,
        blank=True
    )

    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')
        indexes = [
            models.Index(fields=['cost_center']),
            models.Index(fields=['advertiser']),
            models.Index(fields=['payment_type']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['cost_center', 'advertiser', 'payment_type', 'media_unit_type', 'fee_type', 'fee_value_micros'],
                name='ux_payment_methods_signature'
            )
        ]

    def __str__(self):
        if self.payment_type == PaymentTypeEnum.MEDIA_UNIT_TYPE:
            return f"{self.cost_center.name} - {self.media_unit_type.code if self.media_unit_type else 'N/A'}"
        else:
            return f"{self.cost_center.name} - {self.fee_type} Fee"

    @property
    def fee_value(self):
        if self.fee_value_micros:
            return self.fee_value_micros / 1_000_000
        return None


# =============================================================================
# SUBCAMPAIGN PAYMENT TYPE (V100)
# =============================================================================

class SubcampaignPaymentType(BaseModel):
    """
    Subcampaign Payment Type - Fee tracking per subcampaign with date range.
    V100: id uuid [pk], subcampaign_id uuid [not null]

    V100 Changes:
    - Removed: payment_method_id, payment_type, media_unit_type_id
    - Changed: fee_type uses utils_type_enum
    - Changed: fee_value_micros renamed to fee_value
    - Added: is_fee_value_overwritten flag
    - Added: updated_at timestamp
    """
    subcampaign = models.ForeignKey(
        'campaigns.Subcampaign',
        on_delete=models.CASCADE,
        related_name='payment_types',
        verbose_name=_('subcampaign')
    )

    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))

    # V100: fee_type uses utils_type_enum
    fee_type = models.CharField(
        _('fee type'),
        max_length=10,
        choices=UtilsTypeEnum.choices,
        null=True,
        blank=True
    )

    # V100: renamed from fee_value_micros to fee_value
    fee_value = models.BigIntegerField(
        _('fee value'),
        null=True,
        blank=True
    )

    # V100: NEW - flag to track manual overrides
    is_fee_value_overwritten = models.BooleanField(
        _('is fee value overwritten'),
        default=False,
        help_text=_('True if the fee value was manually overridden by user')
    )

    class Meta:
        verbose_name = _('subcampaign payment type')
        verbose_name_plural = _('subcampaign payment types')
        constraints = [
            models.UniqueConstraint(
                fields=['subcampaign', 'start_date', 'end_date'],
                name='ux_subcampaign_payment_type_range'
            )
        ]
        indexes = [
            models.Index(fields=['subcampaign']),
        ]

    def __str__(self):
        return f"{self.subcampaign} - {self.start_date} to {self.end_date}"

    @property
    def fee_value_decimal(self):
        """Returns fee value as decimal (for micros: divide by 1M)"""
        if self.fee_value:
            return self.fee_value / 1_000_000
        return None


# =============================================================================
# PRICING ADJUSTMENT RULE (V100)
# =============================================================================

class PricingAdjustmentRule(BaseModel):
    """
    Pricing Adjustment Rule - Price adjustments with date ranges.
    V100: id uuid [pk], target_kind pricing_adj_target_kind [not null]

    V100 Changes from V67:
    - Removed: media_unit_type_id, payment_method_id FK references
    - Added: payment_method enum field
    - Added: is_adjustment_value_micros_overwritten flag

    Exactly one of (cost_center_id, client_id, advertiser_id) must be NOT NULL
    based on target_kind.
    """
    # Target kind determines which FK is used
    target_kind = models.CharField(
        _('target kind'),
        max_length=20,
        choices=PricingAdjustmentTargetKindEnum.choices
    )

    # Target scope (exactly one must be set based on target_kind)
    cost_center = models.ForeignKey(
        'core.CostCenter',
        on_delete=models.CASCADE,
        related_name='pricing_adjustment_rules',
        verbose_name=_('cost center'),
        null=True,
        blank=True
    )
    client = models.ForeignKey(
        'core.Client',
        on_delete=models.CASCADE,
        related_name='pricing_adjustment_rules',
        verbose_name=_('client'),
        null=True,
        blank=True
    )
    advertiser = models.ForeignKey(
        'core.Advertiser',
        on_delete=models.CASCADE,
        related_name='pricing_adjustment_rules',
        verbose_name=_('advertiser'),
        null=True,
        blank=True
    )

    # Date range for the adjustment
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))

    # V100: NEW - payment method enum (replaces FK to payment_method)
    payment_method = models.CharField(
        _('payment method'),
        max_length=20,
        choices=PaymentMethodEnum.choices,
        null=True,
        blank=True
    )

    # V100: NEW - flag to track manual overrides
    is_adjustment_value_micros_overwritten = models.BooleanField(
        _('is adjustment value overwritten'),
        default=False,
        help_text=_('True if the adjustment value was manually overridden')
    )

    # Adjustment details
    adjustment_kind = models.CharField(
        _('adjustment kind'),
        max_length=30,
        choices=AdjustmentKindEnum.choices
    )
    adjustment_value_micros = models.BigIntegerField(_('adjustment value (micros)'))

    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('pricing adjustment rule')
        verbose_name_plural = _('pricing adjustment rules')
        indexes = [
            models.Index(fields=['target_kind']),
            models.Index(fields=['cost_center']),
            models.Index(fields=['client']),
            models.Index(fields=['advertiser']),
        ]

    def __str__(self):
        scope = self.cost_center or self.client or self.advertiser
        return f"{scope} - {self.adjustment_kind}: {self.adjustment_value_micros}"

    @property
    def adjustment_value(self):
        return self.adjustment_value_micros / 1_000_000

    def clean(self):
        from django.core.exceptions import ValidationError

        # Validate target_kind matches the FK that is set
        if self.target_kind == PricingAdjustmentTargetKindEnum.COST_CENTER:
            if not self.cost_center or self.client or self.advertiser:
                raise ValidationError(
                    _('For target_kind=cost_center, only cost_center must be set.')
                )
        elif self.target_kind == PricingAdjustmentTargetKindEnum.CLIENT:
            if not self.client or self.cost_center or self.advertiser:
                raise ValidationError(
                    _('For target_kind=client, only client must be set.')
                )
        elif self.target_kind == PricingAdjustmentTargetKindEnum.ADVERTISER:
            if not self.advertiser or self.cost_center or self.client:
                raise ValidationError(
                    _('For target_kind=advertiser, only advertiser must be set.')
                )
