"""
Campaigns Admin - Module 4 Administration
Based on EOS Schema V100
"""
from django.contrib import admin
from .models import (
    Project, MediaPlan, Campaign, Subcampaign, SubcampaignVersion
)


# =============================================================================
# PROJECT ADMIN
# =============================================================================

class MediaPlanInline(admin.TabularInline):
    model = MediaPlan
    extra = 0
    fields = ['name', 'status', 'start_date', 'end_date', 'total_budget_micros', 'is_active']
    readonly_fields = []
    show_change_link = True


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'internal_code', 'advertiser', 'status', 'is_active', 'created_at']
    list_filter = ['status', 'is_active', 'advertiser__client__cost_center__agency']
    search_fields = ['name', 'internal_code', 'advertiser__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [MediaPlanInline]

    fieldsets = (
        (None, {
            'fields': ('advertiser', 'name', 'internal_code', 'description', 'status')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# MEDIA PLAN ADMIN
# =============================================================================

class CampaignInline(admin.TabularInline):
    model = Campaign
    extra = 0
    fields = ['campaign_name', 'start_date', 'end_date', 'total_budget_micros', 'is_active']
    readonly_fields = []
    show_change_link = True


@admin.register(MediaPlan)
class MediaPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'total_budget', 'start_date', 'end_date', 'is_active']
    list_filter = ['status', 'is_active']
    search_fields = ['name', 'project__name', 'external_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'total_budget']
    inlines = [CampaignInline]

    fieldsets = (
        (None, {
            'fields': ('project', 'name', 'notes', 'external_id', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Budget', {
            'fields': ('total_budget_micros', 'total_budget')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# CAMPAIGN ADMIN
# =============================================================================

class SubcampaignInline(admin.TabularInline):
    model = Subcampaign
    extra = 0
    fields = ['name', 'subcampaign_code', 'status', 'is_active']
    readonly_fields = ['subcampaign_code']
    show_change_link = True


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['campaign_name', 'internal_campaign_name', 'media_plan', 'total_budget', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'category', 'product', 'language']
    search_fields = ['campaign_name', 'internal_campaign_name', 'external_id', 'media_plan__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'total_budget']
    date_hierarchy = 'start_date'
    inlines = [SubcampaignInline]

    fieldsets = (
        (None, {
            'fields': ('media_plan', 'campaign_name', 'internal_campaign_name', 'external_id')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Categorization', {
            'fields': ('category', 'product', 'language')
        }),
        ('Budget', {
            'fields': ('total_budget_micros', 'total_budget')
        }),
        ('Details', {
            'fields': ('landing_url', 'invoice_reference')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# SUBCAMPAIGN ADMIN
# =============================================================================

class SubcampaignVersionInline(admin.TabularInline):
    model = SubcampaignVersion
    extra = 0
    fields = ['version_number', 'version_name', 'status', 'planned_budget_micros', 'is_active']
    readonly_fields = ['version_number']
    show_change_link = True


@admin.register(Subcampaign)
class SubcampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'subcampaign_code', 'campaign', 'status', 'trafficker_user', 'is_active']
    list_filter = ['status', 'is_active', 'goal', 'publisher', 'tactic', 'country']
    search_fields = ['name', 'subcampaign_code', 'campaign__campaign_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'is_editable']
    inlines = [SubcampaignVersionInline]

    fieldsets = (
        (None, {
            'fields': ('campaign', 'name', 'subcampaign_code', 'objective', 'status')
        }),
        ('Pricing Catalogs', {
            'fields': ('goal', 'publisher', 'tactic', 'creative_type', 'country', 'effort')
        }),
        ('Trafficker', {
            'fields': ('trafficker_user',)
        }),
        ('Custom Labels', {
            'fields': (
                'l5_custom1', 'l8_custom2', 'l9_custom3', 'l11_custom4', 'l13_custom5',
                'l15_custom6', 'l16_custom7', 'l17_custom8', 'l19_custom9', 'l20_custom10'
            ),
            'classes': ('collapse',)
        }),
        ('Geographic', {
            'fields': ('city_geoname_id',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_editable')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# SUBCAMPAIGN VERSION ADMIN
# =============================================================================

@admin.register(SubcampaignVersion)
class SubcampaignVersionAdmin(admin.ModelAdmin):
    list_display = [
        'subcampaign', 'version_number', 'version_name', 'status',
        'planned_budget', 'unit_price', 'is_unit_price_overwritten', 'is_active'
    ]
    list_filter = ['status', 'is_active', 'is_unit_price_overwritten', 'currency', 'media_unit_type']
    search_fields = ['subcampaign__name', 'subcampaign__subcampaign_code', 'version_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'unit_price', 'planned_budget', 'is_editable']

    fieldsets = (
        (None, {
            'fields': ('subcampaign', 'version_number', 'version_name', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Pricing', {
            'fields': (
                'currency', 'media_unit_type', 'performance_pricing_model',
                'unit_price_micros', 'unit_price', 'is_unit_price_overwritten',
                'planned_units', 'planned_budget_micros', 'planned_budget'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'is_editable')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
