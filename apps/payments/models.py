"""
Payments Models - Payment Methods, Pricing/Fee Adjustment Rules
Based on EOS Schema V67

This module implements:
- PaymentMethods (defined by cost_center, optional advertiser override)
- SubcampaignPaymentType (snapshot per version + date range)
- PricingAdjustmentRule (pricing adjustments with date ranges)
- FeeAdjustmentRule (fee adjustments with override capability)

V67 Changes:
- Separated pricing_adjustment_rule and fee_adjustment_rule
- Added date range fields (start_date, end_date) to adjustment rules
- New enum types for adjustment targeting (pricing_adj_target_kind, fee_adj_target_kind)
- Fee adjustments support override with override_fee_type and override_fee_value_micros
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel


# =============================================================================
# ENUMS
# =============================================================================

class PaymentTypeEnum(models.TextChoices):
    MEDIA_UNIT_TYPE = 'media_unit_type', _('Media Unit Type')
    FEE = 'fee', _('Fee')


class FeeTypeEnum(models.TextChoices):
    PCT = 'PCT', _('Percentage')
    FLAT = 'FLAT', _('Flat Amount')


class PricingAdjustmentKindEnum(models.TextChoices):
    """V67: pricing_adj_kind enum"""
    PCT_OF_BASE_MICROS = 'PCT_OF_BASE_MICROS', _('Percentage of Base (Micros)')
    ABS_MICROS = 'ABS_MICROS', _('Absolute (Micros)')
    OVERRIDE_MICROS = 'OVERRIDE_MICROS', _('Override (Micros)')


class PricingAdjustmentTargetKindEnum(models.TextChoices):
    """V67: pricing_adj_target_kind enum"""
    COST_CENTER = 'cost_center', _('Cost Center')
    CLIENT = 'client', _('Client')
    ADVERTISER = 'advertiser', _('Advertiser')


class FeeAdjustmentTargetKindEnum(models.TextChoices):
    """V67: fee_adj_target_kind enum"""
    COST_CENTER = 'cost_center', _('Cost Center')
    CLIENT = 'client', _('Client')
    ADVERTISER = 'advertiser', _('Advertiser')


class FeeAdjustmentKindEnum(models.TextChoices):
    """V67: fee_adj_kind enum"""
    PCT_OF_BASE = 'PCT_OF_BASE', _('Percentage of Base')
    ABS_MICROS = 'ABS_MICROS', _('Absolute (Micros)')
    OVERRIDE = 'OVERRIDE', _('Override')


# =============================================================================
# PAYMENT METHODS
# =============================================================================

class PaymentMethod(BaseModel):
    """
    Payment Method - Defines payment types at cost_center level with optional advertiser override.
    V67: id uuid [pk], cost_center_id uuid [not null], advertiser_id uuid [null]

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
# SUBCAMPAIGN PAYMENT TYPE
# =============================================================================

class SubcampaignPaymentType(BaseModel):
    """
    Subcampaign Payment Type - Assigns payment method per version with date range.
    Stores snapshot for historical accuracy.
    V67: id uuid [pk], subcampaign_version_id uuid [not null]
    """
    subcampaign_version = models.ForeignKey(
        'campaigns.SubcampaignVersion',
        on_delete=models.CASCADE,
        related_name='payment_types',
        verbose_name=_('subcampaign version')
    )

    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))

    # Reference to the payment method
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name='subcampaign_assignments',
        verbose_name=_('payment method')
    )

    # Snapshot fields (copied from payment_method at assignment time)
    payment_type = models.CharField(
        _('payment type'),
        max_length=20,
        choices=PaymentTypeEnum.choices
    )
    media_unit_type = models.ForeignKey(
        'entities.MediaUnitType',
        on_delete=models.PROTECT,
        related_name='payment_type_snapshots',
        verbose_name=_('media unit type'),
        null=True,
        blank=True
    )
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
        verbose_name = _('subcampaign payment type')
        verbose_name_plural = _('subcampaign payment types')
        constraints = [
            models.UniqueConstraint(
                fields=['subcampaign_version', 'start_date', 'end_date'],
                name='ux_subcampaign_payment_type_range'
            )
        ]
        indexes = [
            models.Index(fields=['payment_method']),
            models.Index(fields=['payment_type']),
        ]

    def __str__(self):
        return f"{self.subcampaign_version} - {self.start_date} to {self.end_date}"

    def save(self, *args, **kwargs):
        # Copy snapshot from payment_method if not set
        if self.payment_method and not self.payment_type:
            self.payment_type = self.payment_method.payment_type
            self.media_unit_type = self.payment_method.media_unit_type
            self.fee_type = self.payment_method.fee_type
            self.fee_value_micros = self.payment_method.fee_value_micros
        super().save(*args, **kwargs)


# =============================================================================
# PRICING ADJUSTMENT RULE (V67)
# =============================================================================

class PricingAdjustmentRule(BaseModel):
    """
    Pricing Adjustment Rule - Price adjustments for media_unit_type payment methods.
    V67: id uuid [pk], target_kind pricing_adj_target_kind [not null]

    Applies to payment_method where payment_type = 'media_unit_type'.
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

    # Target payment method (must be media_unit_type)
    target_payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        related_name='pricing_adjustment_rules',
        verbose_name=_('target payment method')
    )

    # Date range for the adjustment
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))

    # Adjustment details
    adjustment_kind = models.CharField(
        _('adjustment kind'),
        max_length=30,
        choices=PricingAdjustmentKindEnum.choices
    )
    adjustment_value_micros = models.BigIntegerField(_('adjustment value (micros)'))

    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('pricing adjustment rule')
        verbose_name_plural = _('pricing adjustment rules')
        indexes = [
            models.Index(fields=['target_payment_method']),
            models.Index(fields=['target_kind']),
            models.Index(fields=['cost_center']),
            models.Index(fields=['client']),
            models.Index(fields=['advertiser']),
            models.Index(fields=['start_date', 'end_date']),
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


# =============================================================================
# FEE ADJUSTMENT RULE (V67)
# =============================================================================

class FeeAdjustmentRule(BaseModel):
    """
    Fee Adjustment Rule - Fee adjustments for fee payment methods.
    V67: id uuid [pk], target_kind fee_adj_target_kind [not null]

    Applies to payment_method where payment_type = 'fee'.
    Exactly one of (cost_center_id, client_id, advertiser_id) must be NOT NULL
    based on target_kind.

    When adjustment_kind = 'OVERRIDE':
    - override_fee_type and override_fee_value_micros must be NOT NULL
    """
    # Target kind determines which FK is used
    target_kind = models.CharField(
        _('target kind'),
        max_length=20,
        choices=FeeAdjustmentTargetKindEnum.choices
    )

    # Target scope (exactly one must be set based on target_kind)
    cost_center = models.ForeignKey(
        'core.CostCenter',
        on_delete=models.CASCADE,
        related_name='fee_adjustment_rules',
        verbose_name=_('cost center'),
        null=True,
        blank=True
    )
    client = models.ForeignKey(
        'core.Client',
        on_delete=models.CASCADE,
        related_name='fee_adjustment_rules',
        verbose_name=_('client'),
        null=True,
        blank=True
    )
    advertiser = models.ForeignKey(
        'core.Advertiser',
        on_delete=models.CASCADE,
        related_name='fee_adjustment_rules',
        verbose_name=_('advertiser'),
        null=True,
        blank=True
    )

    # Target payment method (must be fee type)
    target_payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        related_name='fee_adjustment_rules',
        verbose_name=_('target payment method')
    )

    # Date range for the adjustment
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))

    # Adjustment details
    adjustment_kind = models.CharField(
        _('adjustment kind'),
        max_length=20,
        choices=FeeAdjustmentKindEnum.choices
    )
    adjustment_value_micros = models.BigIntegerField(
        _('adjustment value (micros)'),
        null=True,
        blank=True,
        help_text=_('Used for PCT_OF_BASE and ABS_MICROS kinds')
    )

    # Override fields (used when adjustment_kind = 'OVERRIDE')
    override_fee_type = models.CharField(
        _('override fee type'),
        max_length=10,
        choices=FeeTypeEnum.choices,
        null=True,
        blank=True,
        help_text=_('Required when adjustment_kind is OVERRIDE')
    )
    override_fee_value_micros = models.BigIntegerField(
        _('override fee value (micros)'),
        null=True,
        blank=True,
        help_text=_('Required when adjustment_kind is OVERRIDE')
    )

    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('fee adjustment rule')
        verbose_name_plural = _('fee adjustment rules')
        indexes = [
            models.Index(fields=['target_payment_method']),
            models.Index(fields=['target_kind']),
            models.Index(fields=['cost_center']),
            models.Index(fields=['client']),
            models.Index(fields=['advertiser']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        scope = self.cost_center or self.client or self.advertiser
        return f"{scope} - {self.adjustment_kind}: Fee Adjustment"

    @property
    def adjustment_value(self):
        if self.adjustment_value_micros:
            return self.adjustment_value_micros / 1_000_000
        return None

    @property
    def override_fee_value(self):
        if self.override_fee_value_micros:
            return self.override_fee_value_micros / 1_000_000
        return None

    def clean(self):
        from django.core.exceptions import ValidationError

        # Validate target_kind matches the FK that is set
        if self.target_kind == FeeAdjustmentTargetKindEnum.COST_CENTER:
            if not self.cost_center or self.client or self.advertiser:
                raise ValidationError(
                    _('For target_kind=cost_center, only cost_center must be set.')
                )
        elif self.target_kind == FeeAdjustmentTargetKindEnum.CLIENT:
            if not self.client or self.cost_center or self.advertiser:
                raise ValidationError(
                    _('For target_kind=client, only client must be set.')
                )
        elif self.target_kind == FeeAdjustmentTargetKindEnum.ADVERTISER:
            if not self.advertiser or self.cost_center or self.client:
                raise ValidationError(
                    _('For target_kind=advertiser, only advertiser must be set.')
                )

        # Validate override fields when adjustment_kind is OVERRIDE
        if self.adjustment_kind == FeeAdjustmentKindEnum.OVERRIDE:
            if not self.override_fee_type or self.override_fee_value_micros is None:
                raise ValidationError(
                    _('override_fee_type and override_fee_value_micros are required when adjustment_kind is OVERRIDE.')
                )
