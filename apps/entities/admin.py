from django.contrib import admin
from .models import (
    Entity, AdvertiserEntityBlock, MediaUnitType,
    Goal, Publisher, Tactic, CreativeType, Country,
    PerformancePricingModel, PerformancePricingModelValue, Effort,
    Category, Product, Language,
    GoalPublisher, PublisherTactic, TacticCreativeType,
    CreativeTypeCountry, CategoryProduct, ProductLanguage
)


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ['id', 'entity_name', 'entity_type', 'cost_center', 'created_at']
    list_filter = ['entity_type', 'cost_center']
    search_fields = ['entity_name']
    ordering = ['entity_type', 'entity_name']


@admin.register(MediaUnitType)
class MediaUnitTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']


@admin.register(Tactic)
class TacticAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']


@admin.register(CreativeType)
class CreativeTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'code']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']


@admin.register(Effort)
class EffortAdmin(admin.ModelAdmin):
    list_display = ['id', 'description']


@admin.register(PerformancePricingModel)
class PerformancePricingModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'is_percentage', 'media_unit_type']


@admin.register(PerformancePricingModelValue)
class PerformancePricingModelValueAdmin(admin.ModelAdmin):
    list_display = ['id', 'value_micros']


@admin.register(AdvertiserEntityBlock)
class AdvertiserEntityBlockAdmin(admin.ModelAdmin):
    list_display = ['advertiser', 'entity', 'blocked_at']
    list_filter = ['advertiser']
