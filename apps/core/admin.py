"""
Core Admin - Multi-tenancy and Business Hierarchy Administration
"""
from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import (
    Tenant, Domain, Agency, CostCenter, Client, Advertiser,
    Currency, ExchangeRate, AuditLog
)


@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'default_currency', 'created_at']
    list_filter = ['is_active', 'default_currency']
    search_fields = ['name', 'slug', 'contact_email']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'is_active')
        }),
        ('Settings', {
            'fields': ('default_currency', 'timezone', 'language')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Metadata', {
            'fields': ('logo', 'description')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['domain', 'tenant__name']


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'tenant', 'is_active', 'created_at']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name', 'code', 'contact_email']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('tenant', 'name', 'code', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Settings', {
            'fields': ('default_currency',)
        }),
        ('Metadata', {
            'fields': ('logo', 'description')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'agency', 'annual_budget', 'is_active']
    list_filter = ['is_active', 'agency']
    search_fields = ['name', 'code']
    readonly_fields = ['id', 'created_at', 'updated_at', 'annual_budget']

    fieldsets = (
        (None, {
            'fields': ('agency', 'name', 'code', 'is_active')
        }),
        ('Budget', {
            'fields': ('annual_budget_micros', 'annual_budget')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'agency', 'industry', 'is_active']
    list_filter = ['is_active', 'agency', 'industry']
    search_fields = ['name', 'code', 'contact_email']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('agency', 'cost_center', 'name', 'code', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'contact_email', 'contact_phone', 'address')
        }),
        ('Details', {
            'fields': ('industry', 'website')
        }),
        ('Metadata', {
            'fields': ('logo', 'notes')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Advertiser)
class AdvertiserAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'client', 'brand_name', 'is_active']
    list_filter = ['is_active', 'client__agency', 'category']
    search_fields = ['name', 'code', 'brand_name']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('client', 'name', 'code', 'is_active')
        }),
        ('Brand Information', {
            'fields': ('brand_name', 'category')
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'contact_email')
        }),
        ('Metadata', {
            'fields': ('logo', 'description')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['from_currency', 'to_currency', 'rate', 'effective_date']
    list_filter = ['from_currency', 'to_currency']
    search_fields = ['from_currency__code', 'to_currency__code']
    date_hierarchy = 'effective_date'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'action', 'entity_type', 'user_email', 'entity_name']
    list_filter = ['action', 'entity_type', 'timestamp']
    search_fields = ['entity_name', 'user_email', 'entity_id']
    readonly_fields = [
        'id', 'timestamp', 'user_id', 'user_email', 'action',
        'entity_type', 'entity_id', 'entity_name',
        'old_values', 'new_values', 'ip_address', 'user_agent', 'notes'
    ]
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
