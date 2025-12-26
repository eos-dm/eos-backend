"""
Core Admin - Multi-tenancy and Business Hierarchy Administration
"""
from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import (
    Tenant, Domain, Agency, CostCenter, Client, Advertiser,
    Currency, Timezone, Industry, SystemParameter, SystemVersion, AuditLog
)


@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'code_prefix', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code_prefix']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['domain', 'tenant__name']


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'internal_code', 'tenant', 'code_subcampaign', 'is_active', 'created_at']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name', 'internal_code', 'contact_email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'agency', 'default_currency', 'is_active']
    list_filter = ['is_active', 'agency', 'default_currency']
    search_fields = ['name', 'code', 'internal_code']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'internal_code', 'cost_center', 'status', 'is_active']
    list_filter = ['is_active', 'status', 'cost_center__agency']
    search_fields = ['name', 'internal_code', 'contact_email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Advertiser)
class AdvertiserAdmin(admin.ModelAdmin):
    list_display = ['name', 'internal_code', 'client', 'industry', 'status', 'is_active']
    list_filter = ['is_active', 'status', 'industry', 'client__cost_center__agency']
    search_fields = ['name', 'internal_code', 'contact_email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(Timezone)
class TimezoneAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'utc_offset', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(SystemParameter)
class SystemParameterAdmin(admin.ModelAdmin):
    list_display = ['key', 'is_active', 'effective_from', 'effective_to']
    list_filter = ['is_active']
    search_fields = ['key', 'description']


@admin.register(SystemVersion)
class SystemVersionAdmin(admin.ModelAdmin):
    list_display = ['name', 'applied_at']
    search_fields = ['name']
    date_hierarchy = 'applied_at'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['entity_type', 'entity_id', 'action', 'created_by', 'created_at']
    list_filter = ['action', 'entity_type', 'created_at']
    search_fields = ['entity_id', 'description']
    readonly_fields = [
        'id', 'entity_type', 'entity_id', 'action',
        'description', 'created_by', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
