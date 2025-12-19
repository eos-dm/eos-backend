"""
Entities Models - Polymorphic Entity System for Pricing and Labels
Based on EOS Schema V66

This module implements the entity system with:
- Base Entity table with entity_type discriminator
- Subtype tables (goals, publishers, tactics, etc.)
- Custom label tables (l5_custom1 through l20_custom10)
- Media unit type catalog
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
import uuid


# =============================================================================
# ENTITY TYPE ENUM
# =============================================================================

class EntityType(models.TextChoices):
    GOAL = 'goal', _('Goal')
    PUBLISHER = 'publisher', _('Publisher')
    TACTIC = 'tactic', _('Tactic')
    CREATIVE_TYPE = 'creative_type', _('Creative Type')
    COUNTRY = 'country', _('Country')
    PERFORMANCE_PRICING_MODEL = 'performance_pricing_model', _('Performance Pricing Model')
    PERFORMANCE_PRICING_MODEL_VALUE = 'performance_pricing_model_value', _('Performance Pricing Model Value')
    EFFORT = 'effort', _('Effort')
    CATEGORY = 'category', _('Category')
    PRODUCT = 'product', _('Product')
    LANGUAGE = 'language', _('Language')
    L5_CUSTOM1 = 'l5_custom1', _('Custom Label 1')
    L8_CUSTOM2 = 'l8_custom2', _('Custom Label 2')
    L9_CUSTOM3 = 'l9_custom3', _('Custom Label 3')
    L11_CUSTOM4 = 'l11_custom4', _('Custom Label 4')
    L13_CUSTOM5 = 'l13_custom5', _('Custom Label 5')
    L15_CUSTOM6 = 'l15_custom6', _('Custom Label 6')
    L16_CUSTOM7 = 'l16_custom7', _('Custom Label 7')
    L17_CUSTOM8 = 'l17_custom8', _('Custom Label 8')
    L19_CUSTOM9 = 'l19_custom9', _('Custom Label 9')
    L20_CUSTOM10 = 'l20_custom10', _('Custom Label 10')


# =============================================================================
# BASE ENTITY
# =============================================================================

class Entity(BaseModel):
    """
    Base Entity - Parent table for all entity types.
    V66: id uuid [pk], entity_type entity_type_enum [not null]
    """
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        choices=EntityType.choices,
        db_index=True
    )
    entity_name = models.CharField(_('entity name'), max_length=100, blank=True, null=True)

    # Scope
    cost_center = models.ForeignKey(
        'core.CostCenter',
        on_delete=models.CASCADE,
        related_name='entities',
        verbose_name=_('cost center'),
        null=True,
        blank=True
    )
    owner_advertiser = models.ForeignKey(
        'core.Advertiser',
        on_delete=models.CASCADE,
        related_name='owned_entities',
        verbose_name=_('owner advertiser'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('entity')
        verbose_name_plural = _('entities')
        ordering = ['entity_type', 'entity_name']
        indexes = [
            models.Index(fields=['entity_type']),
            models.Index(fields=['entity_name']),
            models.Index(fields=['cost_center', 'entity_type']),
            models.Index(fields=['owner_advertiser', 'entity_type']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['id', 'entity_type'],
                name='ux_entities_id_type'
            )
        ]

    def __str__(self):
        return f"{self.entity_name} ({self.entity_type})"


class AdvertiserEntityBlock(models.Model):
    """
    Advertiser Entity Block - Block certain entities for specific advertisers.
    V66: advertiser_id uuid [pk], entity_id uuid [pk]
    """
    advertiser = models.ForeignKey(
        'core.Advertiser',
        on_delete=models.CASCADE,
        related_name='blocked_entities',
        verbose_name=_('advertiser')
    )
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='blocked_by_advertisers',
        verbose_name=_('entity')
    )
    blocked_at = models.DateTimeField(_('blocked at'), auto_now_add=True)
    reason = models.TextField(_('reason'), blank=True, null=True)

    class Meta:
        verbose_name = _('advertiser entity block')
        verbose_name_plural = _('advertiser entity blocks')
        constraints = [
            models.UniqueConstraint(
                fields=['advertiser', 'entity'],
                name='pk_advertiser_entity_blocks'
            )
        ]

    def __str__(self):
        return f"{self.advertiser.name} blocks {self.entity.entity_name}"


# =============================================================================
# MEDIA UNIT TYPE (Separate catalog)
# =============================================================================

class MediaUnitType(BaseModel):
    """
    Media Unit Type - CPM, CPC, CPL, CPA, FLAT, etc.
    V66: id uuid [pk], code varchar(20) [unique]
    """
    code = models.CharField(_('code'), max_length=20, unique=True)
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('media unit type')
        verbose_name_plural = _('media unit types')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


# =============================================================================
# ENTITY SUBTYPES - Pricing
# =============================================================================

class Goal(models.Model):
    """
    Goal Entity Subtype.
    V66: id uuid [pk], entity_type = 'goal'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        default=EntityType.GOAL,
        editable=False
    )
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        verbose_name = _('goal')
        verbose_name_plural = _('goals')

    def __str__(self):
        try:
            return self.entity.entity_name or str(self.id)
        except Entity.DoesNotExist:
            return str(self.id)

    @property
    def entity(self):
        return Entity.objects.get(id=self.id, entity_type=EntityType.GOAL)


class Publisher(models.Model):
    """
    Publisher Entity Subtype.
    V66: id uuid [pk], entity_type = 'publisher'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        default=EntityType.PUBLISHER,
        editable=False
    )
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        verbose_name = _('publisher')
        verbose_name_plural = _('publishers')

    def __str__(self):
        try:
            return self.entity.entity_name or str(self.id)
        except Entity.DoesNotExist:
            return str(self.id)


class Tactic(models.Model):
    """
    Tactic Entity Subtype.
    V66: id uuid [pk], entity_type = 'tactic'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        default=EntityType.TACTIC,
        editable=False
    )
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        verbose_name = _('tactic')
        verbose_name_plural = _('tactics')

    def __str__(self):
        try:
            return Entity.objects.get(id=self.id, entity_type=EntityType.TACTIC).entity_name or str(self.id)
        except Entity.DoesNotExist:
            return str(self.id)


class CreativeType(models.Model):
    """
    Creative Type Entity Subtype.
    V66: id uuid [pk], entity_type = 'creative_type'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        default=EntityType.CREATIVE_TYPE,
        editable=False
    )
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        verbose_name = _('creative type')
        verbose_name_plural = _('creative types')

    def __str__(self):
        try:
            return Entity.objects.get(id=self.id, entity_type=EntityType.CREATIVE_TYPE).entity_name or str(self.id)
        except Entity.DoesNotExist:
            return str(self.id)


class Country(models.Model):
    """
    Country Entity Subtype (for pricing, different from geo_country).
    V66: id uuid [pk], entity_type = 'country', code varchar(10)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        default=EntityType.COUNTRY,
        editable=False
    )
    code = models.CharField(_('code'), max_length=10, unique=True)

    class Meta:
        verbose_name = _('country (pricing)')
        verbose_name_plural = _('countries (pricing)')

    def __str__(self):
        return self.code


class PerformancePricingModel(models.Model):
    """
    Performance Pricing Model Entity Subtype.
    V66: id uuid [pk], entity_type = 'performance_pricing_model'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        default=EntityType.PERFORMANCE_PRICING_MODEL,
        editable=False
    )
    code = models.CharField(_('code'), max_length=10, unique=True)
    description = models.TextField(_('description'), blank=True, null=True)
    is_percentage = models.BooleanField(_('is percentage'), default=False)
    media_unit_type = models.ForeignKey(
        MediaUnitType,
        on_delete=models.PROTECT,
        related_name='pricing_models',
        verbose_name=_('media unit type')
    )

    class Meta:
        verbose_name = _('performance pricing model')
        verbose_name_plural = _('performance pricing models')

    def __str__(self):
        return self.code


class PerformancePricingModelValue(models.Model):
    """
    Performance Pricing Model Value Entity Subtype.
    V66: id uuid [pk], entity_type = 'performance_pricing_model_value'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        default=EntityType.PERFORMANCE_PRICING_MODEL_VALUE,
        editable=False
    )
    value_micros = models.BigIntegerField(_('value (micros)'))

    class Meta:
        verbose_name = _('performance pricing model value')
        verbose_name_plural = _('performance pricing model values')

    def __str__(self):
        return f"{self.value_micros / 1_000_000}"


class Effort(models.Model):
    """
    Effort Entity Subtype.
    V66: id uuid [pk], entity_type = 'effort'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        default=EntityType.EFFORT,
        editable=False
    )
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        verbose_name = _('effort')
        verbose_name_plural = _('efforts')

    def __str__(self):
        try:
            return Entity.objects.get(id=self.id, entity_type=EntityType.EFFORT).entity_name or str(self.id)
        except Entity.DoesNotExist:
            return str(self.id)


# =============================================================================
# ENTITY SUBTYPES - Category/Product/Language
# =============================================================================

class Category(models.Model):
    """
    Category Entity Subtype.
    V66: id uuid [pk], entity_type = 'category'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        default=EntityType.CATEGORY,
        editable=False
    )
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        try:
            return Entity.objects.get(id=self.id, entity_type=EntityType.CATEGORY).entity_name or str(self.id)
        except Entity.DoesNotExist:
            return str(self.id)


class Product(models.Model):
    """
    Product Entity Subtype.
    V66: id uuid [pk], entity_type = 'product'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        default=EntityType.PRODUCT,
        editable=False
    )
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self):
        try:
            return Entity.objects.get(id=self.id, entity_type=EntityType.PRODUCT).entity_name or str(self.id)
        except Entity.DoesNotExist:
            return str(self.id)


class Language(models.Model):
    """
    Language Entity Subtype.
    V66: id uuid [pk], entity_type = 'language'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(
        _('entity type'),
        max_length=50,
        default=EntityType.LANGUAGE,
        editable=False
    )
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        verbose_name = _('language')
        verbose_name_plural = _('languages')

    def __str__(self):
        try:
            return Entity.objects.get(id=self.id, entity_type=EntityType.LANGUAGE).entity_name or str(self.id)
        except Entity.DoesNotExist:
            return str(self.id)


# =============================================================================
# CUSTOM LABELS (L5-L20)
# =============================================================================

class L5Custom1(models.Model):
    """Custom Label 1 (L5)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=50, default=EntityType.L5_CUSTOM1, editable=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('custom label 1 (L5)')
        verbose_name_plural = _('custom labels 1 (L5)')


class L8Custom2(models.Model):
    """Custom Label 2 (L8)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=50, default=EntityType.L8_CUSTOM2, editable=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('custom label 2 (L8)')
        verbose_name_plural = _('custom labels 2 (L8)')


class L9Custom3(models.Model):
    """Custom Label 3 (L9)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=50, default=EntityType.L9_CUSTOM3, editable=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('custom label 3 (L9)')
        verbose_name_plural = _('custom labels 3 (L9)')


class L11Custom4(models.Model):
    """Custom Label 4 (L11)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=50, default=EntityType.L11_CUSTOM4, editable=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('custom label 4 (L11)')
        verbose_name_plural = _('custom labels 4 (L11)')


class L13Custom5(models.Model):
    """Custom Label 5 (L13)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=50, default=EntityType.L13_CUSTOM5, editable=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('custom label 5 (L13)')
        verbose_name_plural = _('custom labels 5 (L13)')


class L15Custom6(models.Model):
    """Custom Label 6 (L15)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=50, default=EntityType.L15_CUSTOM6, editable=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('custom label 6 (L15)')
        verbose_name_plural = _('custom labels 6 (L15)')


class L16Custom7(models.Model):
    """Custom Label 7 (L16)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=50, default=EntityType.L16_CUSTOM7, editable=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('custom label 7 (L16)')
        verbose_name_plural = _('custom labels 7 (L16)')


class L17Custom8(models.Model):
    """Custom Label 8 (L17)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=50, default=EntityType.L17_CUSTOM8, editable=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('custom label 8 (L17)')
        verbose_name_plural = _('custom labels 8 (L17)')


class L19Custom9(models.Model):
    """Custom Label 9 (L19)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=50, default=EntityType.L19_CUSTOM9, editable=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('custom label 9 (L19)')
        verbose_name_plural = _('custom labels 9 (L19)')


class L20Custom10(models.Model):
    """Custom Label 10 (L20)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=50, default=EntityType.L20_CUSTOM10, editable=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('custom label 10 (L20)')
        verbose_name_plural = _('custom labels 10 (L20)')


# =============================================================================
# BRIDGE TABLES (N:M Relationships)
# =============================================================================

class GoalPublisher(models.Model):
    """Goal-Publisher bridge table"""
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='publisher_links')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='goal_links')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['goal', 'publisher'], name='pk_goal_publishers')
        ]


class PublisherTactic(models.Model):
    """Publisher-Tactic bridge table"""
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='tactic_links')
    tactic = models.ForeignKey(Tactic, on_delete=models.CASCADE, related_name='publisher_links')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['publisher', 'tactic'], name='pk_publishers_tactics')
        ]


class TacticCreativeType(models.Model):
    """Tactic-CreativeType bridge table"""
    tactic = models.ForeignKey(Tactic, on_delete=models.CASCADE, related_name='creative_type_links')
    creative_type = models.ForeignKey(CreativeType, on_delete=models.CASCADE, related_name='tactic_links')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tactic', 'creative_type'], name='pk_tactic_creative_types')
        ]


class CreativeTypeCountry(models.Model):
    """CreativeType-Country bridge table"""
    creative_type = models.ForeignKey(CreativeType, on_delete=models.CASCADE, related_name='country_links')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='creative_type_links')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['creative_type', 'country'], name='pk_creative_type_countries')
        ]


class CountryPerformancePricingModel(models.Model):
    """Country-PerformancePricingModel bridge table"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='pricing_model_links')
    performance_pricing_model = models.ForeignKey(
        PerformancePricingModel,
        on_delete=models.CASCADE,
        related_name='country_links'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['country', 'performance_pricing_model'],
                name='pk_countries_performance_pricing_models'
            )
        ]


class PerformancePricingModelValue_Link(models.Model):
    """PerformancePricingModel-Value bridge table"""
    performance_pricing_model = models.ForeignKey(
        PerformancePricingModel,
        on_delete=models.CASCADE,
        related_name='value_links'
    )
    performance_pricing_model_value = models.ForeignKey(
        PerformancePricingModelValue,
        on_delete=models.CASCADE,
        related_name='model_links'
    )

    class Meta:
        db_table = 'entities_perf_pricing_model_value'
        constraints = [
            models.UniqueConstraint(
                fields=['performance_pricing_model', 'performance_pricing_model_value'],
                name='pk_perf_pricing_models_values'
            )
        ]


class GoalEffort(models.Model):
    """Goal-Effort bridge table"""
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='effort_links')
    effort = models.ForeignKey(Effort, on_delete=models.CASCADE, related_name='goal_links')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['goal', 'effort'], name='pk_goal_efforts')
        ]


class CategoryProduct(models.Model):
    """Category-Product bridge table"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_links')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='category_links')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['category', 'product'], name='pk_category_products')
        ]


class ProductLanguage(models.Model):
    """Product-Language bridge table"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='language_links')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='product_links')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'language'], name='pk_product_languages')
        ]
