"""
Core Models - Multi-tenancy Foundation and Business Hierarchy
Based on EOS Schema V66

Hierarchy:
Tenant → Agency → CostCenter → Client → Advertiser → Project → MediaPlan → Campaign → Subcampaign → SubcampaignVersion
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django_tenants.models import TenantMixin, DomainMixin
import uuid


# =============================================================================
# ABSTRACT BASE MODELS
# =============================================================================

class TimeStampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Abstract base model with UUID primary key."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """Abstract base model combining UUID and timestamps."""
    class Meta:
        abstract = True


# =============================================================================
# REFERENCE TABLES
# =============================================================================

class Currency(models.Model):
    """
    Currency - ISO 4217 currency codes.
    V66: code char(3) [pk]
    """
    code = models.CharField(_('code'), max_length=3, primary_key=True)
    name = models.CharField(_('name'), max_length=50)
    symbol = models.CharField(_('symbol'), max_length=10)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('currency')
        verbose_name_plural = _('currencies')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Timezone(models.Model):
    """
    Timezone - Standard timezone codes.
    V66: code varchar(100) [pk]
    """
    code = models.CharField(_('code'), max_length=100, primary_key=True)
    name = models.CharField(_('name'), max_length=100)
    utc_offset = models.CharField(_('UTC offset'), max_length=6)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('timezone')
        verbose_name_plural = _('timezones')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} ({self.utc_offset})"


class Industry(BaseModel):
    """
    Industry - Business industry categories.
    V66: id uuid [pk]
    """
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=50, blank=True, null=True)
    description = models.TextField(_('description'), blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('industry')
        verbose_name_plural = _('industries')
        ordering = ['name']

    def __str__(self):
        return self.name


# =============================================================================
# MULTI-TENANCY MODELS
# =============================================================================

class Tenant(TenantMixin, BaseModel):
    """
    Tenant Model - Root of multi-tenancy hierarchy.
    V66: id uuid [pk], name varchar(255), code_prefix varchar(4)
    """
    name = models.CharField(_('name'), max_length=255)
    code_prefix = models.CharField(
        _('code prefix'),
        max_length=4,
        unique=True,
        help_text=_('4-character prefix for generating codes')
    )
    is_active = models.BooleanField(_('is active'), default=True)

    # auto_create_schema from TenantMixin
    auto_create_schema = True

    class Meta:
        verbose_name = _('tenant')
        verbose_name_plural = _('tenants')
        ordering = ['name']

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    """
    Domain Model - Maps domains to tenants.
    """
    pass


# =============================================================================
# BUSINESS HIERARCHY MODELS
# =============================================================================

class Agency(BaseModel):
    """
    Agency Model - Business unit within a tenant.
    V66: id uuid [pk], tenant_id uuid [not null], name varchar(50)
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='agencies',
        verbose_name=_('tenant')
    )
    name = models.CharField(_('name'), max_length=50)
    internal_code = models.CharField(_('internal code'), max_length=50)
    description = models.TextField(_('description'), blank=True, null=True)
    code_subcampaign = models.CharField(
        _('subcampaign code'),
        max_length=4,
        help_text=_('4-character code for subcampaigns')
    )

    # Timezone
    timezone = models.ForeignKey(
        Timezone,
        on_delete=models.SET_NULL,
        related_name='agencies',
        verbose_name=_('timezone'),
        null=True,
        blank=True,
        db_column='timezone_code'
    )

    # Address
    address_line1 = models.CharField(_('address line 1'), max_length=255, blank=True, null=True)
    address_line2 = models.CharField(_('address line 2'), max_length=255, blank=True, null=True)
    address_postal_code = models.CharField(_('postal code'), max_length=20, blank=True, null=True)
    address_city_geoname_id = models.IntegerField(_('city geoname ID'), blank=True, null=True)
    address_country_code = models.CharField(_('country code'), max_length=2, blank=True, null=True)

    # Contact
    contact_name = models.CharField(_('contact name'), max_length=255, blank=True, null=True)
    contact_email = models.EmailField(_('contact email'), blank=True, null=True)
    contact_phone = models.CharField(_('contact phone'), max_length=50, blank=True, null=True)

    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('agency')
        verbose_name_plural = _('agencies')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'internal_code'],
                name='ux_agency_tenant_code'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.internal_code})"


class CostCenter(BaseModel):
    """
    Cost Center Model - Financial grouping within an agency.
    V66: id uuid [pk], agency_id uuid [not null], code varchar(50)
    """
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name='cost_centers',
        verbose_name=_('agency')
    )
    code = models.CharField(_('code'), max_length=50)
    name = models.CharField(_('name'), max_length=50)
    description = models.TextField(_('description'), blank=True, null=True)
    internal_code = models.CharField(_('internal code'), max_length=50)

    # Currency
    default_currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='cost_centers',
        verbose_name=_('default currency'),
        db_column='default_currency_code'
    )

    # Billing
    payment_terms_days = models.IntegerField(_('payment terms (days)'), blank=True, null=True)
    billing_email = models.EmailField(_('billing email'), blank=True, null=True)
    legal_entity_name = models.CharField(_('legal entity name'), max_length=255, blank=True, null=True)
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True, null=True)
    tax_country_code = models.CharField(_('tax country code'), max_length=2, blank=True, null=True)

    # Address
    address_line1 = models.CharField(_('address line 1'), max_length=255, blank=True, null=True)
    address_line2 = models.CharField(_('address line 2'), max_length=255, blank=True, null=True)
    address_postal_code = models.CharField(_('postal code'), max_length=20, blank=True, null=True)
    address_city_geoname_id = models.IntegerField(_('city geoname ID'), blank=True, null=True)
    address_country_code = models.CharField(_('country code'), max_length=2, blank=True, null=True)

    # Billing Contact
    billing_contact_name = models.CharField(_('billing contact name'), max_length=255, blank=True, null=True)
    billing_contact_phone = models.CharField(_('billing contact phone'), max_length=50, blank=True, null=True)

    # Timezone
    timezone = models.ForeignKey(
        Timezone,
        on_delete=models.SET_NULL,
        related_name='cost_centers',
        verbose_name=_('timezone'),
        null=True,
        blank=True,
        db_column='timezone_code'
    )

    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('cost center')
        verbose_name_plural = _('cost centers')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['agency', 'code'],
                name='ux_cost_center_agency_code'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Client(BaseModel):
    """
    Client Model - Business client of a cost center.
    V66: id uuid [pk], cost_center_id uuid [not null]
    """
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('suspended', _('Suspended')),
    ]

    cost_center = models.ForeignKey(
        CostCenter,
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name=_('cost center')
    )

    name = models.CharField(_('name'), max_length=50)
    description = models.TextField(_('description'), blank=True, null=True)
    external_id = models.CharField(_('external ID'), max_length=100, blank=True, null=True)
    internal_code = models.CharField(_('internal code'), max_length=50)

    # Currency for display
    currency_show = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='clients_display',
        verbose_name=_('display currency'),
        db_column='currency_code_show'
    )

    # Timezone
    timezone = models.ForeignKey(
        Timezone,
        on_delete=models.SET_NULL,
        related_name='clients',
        verbose_name=_('timezone'),
        null=True,
        blank=True,
        db_column='timezone_code'
    )

    # Address
    address_line1 = models.CharField(_('address line 1'), max_length=255, blank=True, null=True)
    address_line2 = models.CharField(_('address line 2'), max_length=255, blank=True, null=True)
    address_postal_code = models.CharField(_('postal code'), max_length=20, blank=True, null=True)
    address_city_geoname_id = models.IntegerField(_('city geoname ID'), blank=True, null=True)

    # Contact
    contact_name = models.CharField(_('contact name'), max_length=255, blank=True, null=True)
    contact_position = models.CharField(_('contact position'), max_length=255, blank=True, null=True)
    contact_phone = models.CharField(_('contact phone'), max_length=50, blank=True, null=True)
    contact_phone_alt = models.CharField(_('alt contact phone'), max_length=50, blank=True, null=True)
    contact_email = models.EmailField(_('contact email'), blank=True, null=True)
    contact_email_alt = models.EmailField(_('alt contact email'), blank=True, null=True)

    # Billing overrides
    payment_terms_days_override = models.IntegerField(_('payment terms override'), blank=True, null=True)
    billing_email_override = models.EmailField(_('billing email override'), blank=True, null=True)

    # Credit
    credit_limit_amount_micros = models.BigIntegerField(_('credit limit (micros)'), blank=True, null=True)
    credit_risk_level = models.CharField(_('credit risk level'), max_length=30, blank=True, null=True)

    status = models.CharField(_('status'), max_length=30, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['cost_center', 'name'],
                name='ux_client_cost_center_name'
            )
        ]

    def __str__(self):
        return f"{self.name}"


class Advertiser(BaseModel):
    """
    Advertiser Model - Brand/Advertiser within a client.
    V66: id uuid [pk], client_id uuid [not null]
    """
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('suspended', _('Suspended')),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='advertisers',
        verbose_name=_('client')
    )

    name = models.CharField(_('name'), max_length=255)
    internal_code = models.CharField(_('internal code'), max_length=50)
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True, null=True)

    # Address
    address_line1 = models.CharField(_('address line 1'), max_length=255, blank=True, null=True)
    address_line2 = models.CharField(_('address line 2'), max_length=255, blank=True, null=True)
    address_postal_code = models.CharField(_('postal code'), max_length=20, blank=True, null=True)
    address_city_geoname_id = models.IntegerField(_('city geoname ID'), blank=True, null=True)
    address_country_code = models.CharField(_('country code'), max_length=2, blank=True, null=True)

    # Contact
    contact_name = models.CharField(_('contact name'), max_length=255, blank=True, null=True)
    contact_email = models.EmailField(_('contact email'), blank=True, null=True)
    contact_phone = models.CharField(_('contact phone'), max_length=50, blank=True, null=True)
    contact_phone_alt = models.CharField(_('alt contact phone'), max_length=50, blank=True, null=True)
    contact_email_alt = models.EmailField(_('alt contact email'), blank=True, null=True)

    # Industry
    industry = models.ForeignKey(
        Industry,
        on_delete=models.PROTECT,
        related_name='advertisers',
        verbose_name=_('industry')
    )

    status = models.CharField(_('status'), max_length=30, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('advertiser')
        verbose_name_plural = _('advertisers')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['client', 'name'],
                name='ux_advertiser_client_name'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.internal_code})"


# =============================================================================
# SYSTEM TABLES
# =============================================================================

class SystemParameter(BaseModel):
    """
    System Parameter - Global configuration parameters.
    V66: key varchar(100) [unique]
    """
    key = models.CharField(_('key'), max_length=100, unique=True)
    value = models.TextField(_('value'))
    description = models.TextField(_('description'), blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)
    effective_from = models.DateTimeField(_('effective from'), blank=True, null=True)
    effective_to = models.DateTimeField(_('effective to'), blank=True, null=True)

    class Meta:
        verbose_name = _('system parameter')
        verbose_name_plural = _('system parameters')
        ordering = ['key']

    def __str__(self):
        return self.key


class SystemVersion(BaseModel):
    """
    System Version - Track schema/system versions.
    V66: name varchar(100)
    """
    name = models.CharField(_('name'), max_length=100)
    applied_at = models.DateTimeField(_('applied at'), auto_now_add=True)
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        verbose_name = _('system version')
        verbose_name_plural = _('system versions')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.name} - {self.applied_at}"


# AuditLog moved to apps.audit.models to avoid circular dependency
