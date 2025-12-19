"""
Campaigns Models - Projects, Media Plans, Campaigns, Subcampaigns
Based on EOS Schema V67

Hierarchy:
Project → MediaPlan → Campaign → Subcampaign → SubcampaignVersion

V67 Changes:
- media_unit_type moved from Subcampaign to SubcampaignVersion only
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel


# =============================================================================
# PROJECT
# =============================================================================

class Project(BaseModel):
    """
    Project Model - Container for media plans.
    V66: id uuid [pk], advertiser_id uuid [not null]
    """
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('paused', _('Paused')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    advertiser = models.ForeignKey(
        'core.Advertiser',
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name=_('advertiser')
    )

    internal_code = models.CharField(_('internal code'), max_length=50)
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True, null=True)
    status = models.CharField(
        _('status'),
        max_length=30,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['advertiser', 'internal_code'],
                name='ux_project_advertiser_code'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.internal_code})"


# =============================================================================
# MEDIA PLAN
# =============================================================================

class MediaPlan(BaseModel):
    """
    Media Plan Model - Planning container for campaigns.
    V66: id uuid [pk], project_id uuid [not null]
    """
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending_review', _('Pending Review')),
        ('approved', _('Approved')),
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='media_plans',
        verbose_name=_('project')
    )

    name = models.CharField(_('name'), max_length=255)
    notes = models.TextField(_('notes'), blank=True, null=True)
    external_id = models.CharField(_('external ID'), max_length=100, blank=True, null=True)

    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))

    status = models.CharField(
        _('status'),
        max_length=30,
        choices=STATUS_CHOICES,
        default='draft'
    )
    total_budget_micros = models.BigIntegerField(_('total budget (micros)'))
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('media plan')
        verbose_name_plural = _('media plans')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}"

    @property
    def total_budget(self):
        return self.total_budget_micros / 1_000_000


# =============================================================================
# CAMPAIGN
# =============================================================================

class Campaign(BaseModel):
    """
    Campaign Model - Marketing campaign within a media plan.
    V66: id uuid [pk], media_plan_id uuid [not null]
    """
    media_plan = models.ForeignKey(
        MediaPlan,
        on_delete=models.CASCADE,
        related_name='campaigns',
        verbose_name=_('media plan')
    )

    campaign_name = models.CharField(_('campaign name'), max_length=100)
    internal_campaign_name = models.CharField(_('internal campaign name'), max_length=100)
    external_id = models.CharField(_('external ID'), max_length=100, blank=True, null=True)
    landing_url = models.URLField(_('landing URL'), max_length=500, blank=True, null=True)

    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))

    # L3/L4/L10 - Category/Product/Language from entities
    category = models.ForeignKey(
        'entities.Category',
        on_delete=models.PROTECT,
        related_name='campaigns',
        verbose_name=_('category')
    )
    product = models.ForeignKey(
        'entities.Product',
        on_delete=models.PROTECT,
        related_name='campaigns',
        verbose_name=_('product')
    )
    language = models.ForeignKey(
        'entities.Language',
        on_delete=models.PROTECT,
        related_name='campaigns',
        verbose_name=_('language')
    )

    total_budget_micros = models.BigIntegerField(_('total budget (micros)'))
    invoice_reference = models.CharField(_('invoice reference'), max_length=100, blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('campaign')
        verbose_name_plural = _('campaigns')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['product']),
            models.Index(fields=['language']),
        ]

    def __str__(self):
        return f"{self.campaign_name}"

    @property
    def total_budget(self):
        return self.total_budget_micros / 1_000_000


# =============================================================================
# SUBCAMPAIGN
# =============================================================================

class Subcampaign(BaseModel):
    """
    Subcampaign Model - Individual channel/platform allocation.
    V67: id uuid [pk], campaign_id uuid [not null]
    Note: media_unit_type moved to SubcampaignVersion in V67
    """
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending_review', _('Pending Review')),
        ('approved', _('Approved')),
        ('active', _('Active')),
        ('paused', _('Paused')),
        ('completed', _('Completed')),
    ]

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='subcampaigns',
        verbose_name=_('campaign')
    )

    name = models.CharField(_('name'), max_length=300)
    subcampaign_code = models.CharField(_('subcampaign code'), max_length=255, unique=True)
    objective = models.TextField(_('objective'), blank=True, null=True)

    # Pricing catalogs (NOT NULL)
    goal = models.ForeignKey(
        'entities.Goal',
        on_delete=models.PROTECT,
        related_name='subcampaigns',
        verbose_name=_('goal')
    )
    publisher = models.ForeignKey(
        'entities.Publisher',
        on_delete=models.PROTECT,
        related_name='subcampaigns',
        verbose_name=_('publisher')
    )
    tactic = models.ForeignKey(
        'entities.Tactic',
        on_delete=models.PROTECT,
        related_name='subcampaigns',
        verbose_name=_('tactic')
    )
    creative_type = models.ForeignKey(
        'entities.CreativeType',
        on_delete=models.PROTECT,
        related_name='subcampaigns',
        verbose_name=_('creative type')
    )
    country = models.ForeignKey(
        'entities.Country',
        on_delete=models.PROTECT,
        related_name='subcampaigns',
        verbose_name=_('country')
    )

    # Effort
    effort = models.ForeignKey(
        'entities.Effort',
        on_delete=models.PROTECT,
        related_name='subcampaigns',
        verbose_name=_('effort')
    )

    # Trafficker
    trafficker_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='trafficked_subcampaigns',
        verbose_name=_('trafficker'),
        null=True,
        blank=True
    )

    # Custom Labels (L5-L20)
    l5_custom1 = models.ForeignKey(
        'entities.L5Custom1', on_delete=models.SET_NULL,
        related_name='subcampaigns', null=True, blank=True
    )
    l8_custom2 = models.ForeignKey(
        'entities.L8Custom2', on_delete=models.SET_NULL,
        related_name='subcampaigns', null=True, blank=True
    )
    l9_custom3 = models.ForeignKey(
        'entities.L9Custom3', on_delete=models.SET_NULL,
        related_name='subcampaigns', null=True, blank=True
    )
    l11_custom4 = models.ForeignKey(
        'entities.L11Custom4', on_delete=models.SET_NULL,
        related_name='subcampaigns', null=True, blank=True
    )
    l13_custom5 = models.ForeignKey(
        'entities.L13Custom5', on_delete=models.SET_NULL,
        related_name='subcampaigns', null=True, blank=True
    )
    l15_custom6 = models.ForeignKey(
        'entities.L15Custom6', on_delete=models.SET_NULL,
        related_name='subcampaigns', null=True, blank=True
    )
    l16_custom7 = models.ForeignKey(
        'entities.L16Custom7', on_delete=models.SET_NULL,
        related_name='subcampaigns', null=True, blank=True
    )
    l17_custom8 = models.ForeignKey(
        'entities.L17Custom8', on_delete=models.SET_NULL,
        related_name='subcampaigns', null=True, blank=True
    )
    l19_custom9 = models.ForeignKey(
        'entities.L19Custom9', on_delete=models.SET_NULL,
        related_name='subcampaigns', null=True, blank=True
    )
    l20_custom10 = models.ForeignKey(
        'entities.L20Custom10', on_delete=models.SET_NULL,
        related_name='subcampaigns', null=True, blank=True
    )

    # Geographic
    city_geoname_id = models.IntegerField(_('city geoname ID'))

    status = models.CharField(
        _('status'),
        max_length=30,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('subcampaign')
        verbose_name_plural = _('subcampaigns')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trafficker_user']),
        ]

    def __str__(self):
        return f"{self.name} ({self.subcampaign_code})"


# =============================================================================
# SUBCAMPAIGN VERSION
# =============================================================================

class SubcampaignVersion(BaseModel):
    """
    Subcampaign Version - Tracks budget/date versions of a subcampaign.
    V67: id uuid [pk], subcampaign_id uuid [not null]
    V67 Change: media_unit_type is now defined per version (NOT NULL)
    """
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    subcampaign = models.ForeignKey(
        Subcampaign,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name=_('subcampaign')
    )

    version_number = models.IntegerField(_('version number'))
    version_name = models.CharField(_('version name'), max_length=255, blank=True, null=True)

    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))

    status = models.CharField(
        _('status'),
        max_length=30,
        choices=STATUS_CHOICES,
        default='draft'
    )

    # V67: unit type per version (NOT NULL) - moved from Subcampaign
    media_unit_type = models.ForeignKey(
        'entities.MediaUnitType',
        on_delete=models.PROTECT,
        related_name='subcampaign_versions',
        verbose_name=_('media unit type')
    )

    unit_price_micros = models.BigIntegerField(_('unit price (micros)'))
    planned_units = models.DecimalField(_('planned units'), max_digits=18, decimal_places=4)
    planned_budget_micros = models.BigIntegerField(_('planned budget (micros)'))

    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('subcampaign version')
        verbose_name_plural = _('subcampaign versions')
        ordering = ['-version_number']
        constraints = [
            models.UniqueConstraint(
                fields=['subcampaign', 'version_number'],
                name='ux_subcampaign_version_sub_vn'
            )
        ]
        indexes = [
            models.Index(fields=['media_unit_type']),
        ]

    def __str__(self):
        return f"{self.subcampaign.name} v{self.version_number}"

    @property
    def unit_price(self):
        return self.unit_price_micros / 1_000_000

    @property
    def planned_budget(self):
        return self.planned_budget_micros / 1_000_000
