"""
Campaigns Admin - Module 4 Administration
"""
from django.contrib import admin
from .models import (
    Project, Campaign, MediaPlan, Subcampaign,
    SubcampaignVersion, SubcampaignFee, CampaignComment, CampaignDocument
)


class CampaignInline(admin.TabularInline):
    model = Campaign
    extra = 0
    fields = ['name', 'code', 'status', 'start_date', 'end_date', 'budget_micros']
    readonly_fields = ['code']
    show_change_link = True


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'advertiser', 'status', 'start_date', 'end_date', 'budget']
    list_filter = ['status', 'is_template', 'advertiser__client__agency']
    search_fields = ['name', 'code', 'advertiser__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'budget']
    date_hierarchy = 'created_at'
    inlines = [CampaignInline]

    fieldsets = (
        (None, {
            'fields': ('advertiser', 'name', 'code', 'description', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Budget', {
            'fields': ('budget_micros', 'budget', 'currency')
        }),
        ('Team', {
            'fields': ('owner', 'planner')
        }),
        ('Metadata', {
            'fields': ('notes', 'is_template')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class MediaPlanInline(admin.TabularInline):
    model = MediaPlan
    extra = 0
    fields = ['name', 'version', 'status', 'total_budget_micros', 'is_active_version']
    readonly_fields = ['version']
    show_change_link = True


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'project', 'status', 'objective', 'start_date', 'end_date', 'budget']
    list_filter = ['status', 'objective', 'is_template', 'project__advertiser__client__agency']
    search_fields = ['name', 'code', 'project__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'budget', 'duration_days']
    date_hierarchy = 'start_date'
    inlines = [MediaPlanInline]

    fieldsets = (
        (None, {
            'fields': ('project', 'name', 'code', 'description', 'status', 'objective')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'duration_days')
        }),
        ('Budget', {
            'fields': ('budget_micros', 'budget', 'currency')
        }),
        ('Targeting', {
            'fields': ('target_audience', 'target_countries', 'target_kpis')
        }),
        ('Team', {
            'fields': ('owner',)
        }),
        ('Metadata', {
            'fields': ('notes', 'is_template')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class SubcampaignInline(admin.TabularInline):
    model = Subcampaign
    extra = 0
    fields = ['name', 'code', 'channel', 'platform', 'status', 'budget_micros']
    readonly_fields = ['code']
    show_change_link = True


@admin.register(MediaPlan)
class MediaPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'campaign', 'status', 'total_budget', 'is_active_version']
    list_filter = ['status', 'is_active_version']
    search_fields = ['name', 'campaign__name']
    readonly_fields = ['id', 'version', 'created_at', 'updated_at', 'total_budget']
    inlines = [SubcampaignInline]

    fieldsets = (
        (None, {
            'fields': ('campaign', 'name', 'version', 'description', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Budget', {
            'fields': ('total_budget_micros', 'total_budget', 'currency')
        }),
        ('Approvals', {
            'fields': ('created_by', 'approved_by', 'approved_at', 'client_approved_by', 'client_approved_at')
        }),
        ('Metadata', {
            'fields': ('notes', 'is_active_version')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class SubcampaignFeeInline(admin.TabularInline):
    model = SubcampaignFee
    extra = 0
    fields = ['name', 'fee_type', 'calculation_method', 'percentage', 'calculated_amount_micros']


@admin.register(Subcampaign)
class SubcampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'media_plan', 'channel', 'platform', 'status', 'budget']
    list_filter = ['status', 'channel', 'platform', 'buying_type']
    search_fields = ['name', 'code', 'media_plan__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'budget', 'unit_price']
    inlines = [SubcampaignFeeInline]

    fieldsets = (
        (None, {
            'fields': ('media_plan', 'name', 'code', 'description', 'status')
        }),
        ('Channel/Platform', {
            'fields': ('channel', 'platform')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Budget & Buying', {
            'fields': ('budget_micros', 'budget', 'currency', 'buying_type', 'unit_price_micros', 'unit_price', 'estimated_units')
        }),
        ('Targeting', {
            'fields': ('target_audience', 'target_locations', 'target_devices')
        }),
        ('Creative', {
            'fields': ('creative_format', 'creative_sizes')
        }),
        ('External Integration', {
            'fields': ('external_id', 'external_account_id')
        }),
        ('Metadata', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SubcampaignVersion)
class SubcampaignVersionAdmin(admin.ModelAdmin):
    list_display = ['subcampaign', 'version_number', 'status', 'budget_micros', 'changed_by', 'created_at']
    list_filter = ['status']
    search_fields = ['subcampaign__name']
    readonly_fields = ['id', 'created_at']


@admin.register(SubcampaignFee)
class SubcampaignFeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'subcampaign', 'fee_type', 'calculation_method', 'calculated_amount']
    list_filter = ['fee_type', 'calculation_method', 'is_included_in_budget']
    search_fields = ['name', 'subcampaign__name']


@admin.register(CampaignComment)
class CampaignCommentAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal']
    search_fields = ['campaign__name', 'author__email', 'content']


@admin.register(CampaignDocument)
class CampaignDocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign', 'document_type', 'uploaded_by', 'is_client_visible', 'created_at']
    list_filter = ['document_type', 'is_client_visible']
    search_fields = ['name', 'campaign__name']
