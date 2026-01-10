"""
Entities Admin - Polymorphic Entity System Administration
Based on EOS Schema V100
"""
from django.contrib import admin
from .models import (
    Entity, AdvertiserEntityBlock, MediaUnitType,
    Goal, Publisher, Tactic, CreativeType, Country,
    PerformancePricingModel, PerformancePricingModelValue, Effort,
    Category, Product, Language,
    GoalPublisher, PublisherTactic, TacticCreativeType,
    CreativeTypeCountry, CategoryProduct, ProductLanguage,
    CountryPerformancePricingModel, GoalEffort
)


# =============================================================================
# BASE ENTITY
# =============================================================================

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ['id', 'entity_name', 'entity_type', 'cost_center', 'owner_advertiser', 'created_at']
    list_filter = ['entity_type', 'cost_center']
    search_fields = ['entity_name']
    ordering = ['entity_type', 'entity_name']


@admin.register(AdvertiserEntityBlock)
class AdvertiserEntityBlockAdmin(admin.ModelAdmin):
    list_display = ['advertiser', 'entity', 'blocked_at', 'reason']
    list_filter = ['advertiser', 'blocked_at']
    search_fields = ['advertiser__name', 'entity__entity_name', 'reason']


# =============================================================================
# MEDIA UNIT TYPE
# =============================================================================

@admin.register(MediaUnitType)
class MediaUnitTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'description', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name', 'description']


# =============================================================================
# PRICING ENTITIES
# =============================================================================

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']
    search_fields = ['description']


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']
    search_fields = ['description']


@admin.register(Tactic)
class TacticAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']
    search_fields = ['description']


@admin.register(CreativeType)
class CreativeTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']
    search_fields = ['description']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'code']
    search_fields = ['code']


@admin.register(Effort)
class EffortAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']
    search_fields = ['description']


# =============================================================================
# CATEGORY/PRODUCT/LANGUAGE
# =============================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']
    search_fields = ['description']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']
    search_fields = ['description']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']
    search_fields = ['description']


# =============================================================================
# PERFORMANCE PRICING (V100)
# =============================================================================

class PerformancePricingModelValueInline(admin.TabularInline):
    model = PerformancePricingModelValue
    extra = 0
    fields = ['value_micros', 'start_date', 'end_date']


@admin.register(PerformancePricingModel)
class PerformancePricingModelAdmin(admin.ModelAdmin):
    """
    V100: Updated to reflect schema changes.
    - Removed is_percentage field
    - Added cost_center, media_unit_type, default_payment_method
    """
    list_display = [
        'id', 'cost_center', 'payment_type', 'media_unit_type',
        'default_payment_method', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'payment_type', 'default_payment_method', 'cost_center']
    search_fields = ['cost_center__name', 'media_unit_type__code']
    inlines = [PerformancePricingModelValueInline]

    fieldsets = (
        (None, {
            'fields': ('cost_center', 'payment_type', 'media_unit_type', 'default_payment_method')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(PerformancePricingModelValue)
class PerformancePricingModelValueAdmin(admin.ModelAdmin):
    """
    V100: Updated to reflect schema changes.
    - Added performance_pricing_model reference
    - Added start_date and end_date fields
    """
    list_display = [
        'id', 'performance_pricing_model', 'value_micros',
        'value', 'start_date', 'end_date', 'created_at'
    ]
    list_filter = ['performance_pricing_model', 'start_date', 'end_date']
    search_fields = ['performance_pricing_model__cost_center__name']
    date_hierarchy = 'start_date'

    fieldsets = (
        (None, {
            'fields': ('performance_pricing_model', 'value_micros')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
    )


# =============================================================================
# BRIDGE TABLES
# =============================================================================

@admin.register(GoalPublisher)
class GoalPublisherAdmin(admin.ModelAdmin):
    list_display = ['goal', 'publisher']
    list_filter = ['goal', 'publisher']


@admin.register(PublisherTactic)
class PublisherTacticAdmin(admin.ModelAdmin):
    list_display = ['publisher', 'tactic']
    list_filter = ['publisher', 'tactic']


@admin.register(TacticCreativeType)
class TacticCreativeTypeAdmin(admin.ModelAdmin):
    list_display = ['tactic', 'creative_type']
    list_filter = ['tactic', 'creative_type']


@admin.register(CreativeTypeCountry)
class CreativeTypeCountryAdmin(admin.ModelAdmin):
    list_display = ['creative_type', 'country']
    list_filter = ['creative_type', 'country']


@admin.register(CategoryProduct)
class CategoryProductAdmin(admin.ModelAdmin):
    list_display = ['category', 'product']
    list_filter = ['category', 'product']


@admin.register(ProductLanguage)
class ProductLanguageAdmin(admin.ModelAdmin):
    list_display = ['product', 'language']
    list_filter = ['product', 'language']


@admin.register(CountryPerformancePricingModel)
class CountryPerformancePricingModelAdmin(admin.ModelAdmin):
    list_display = ['country', 'performance_pricing_model']
    list_filter = ['country']


@admin.register(GoalEffort)
class GoalEffortAdmin(admin.ModelAdmin):
    list_display = ['goal', 'effort']
    list_filter = ['goal', 'effort']
