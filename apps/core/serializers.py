"""
Core Serializers - Multi-tenancy and Business Hierarchy API
"""
from rest_framework import serializers
from .models import (
    Tenant, Agency, CostCenter, Client, Advertiser,
    Currency, ExchangeRate, AuditLog
)


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model."""
    agencies_count = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'is_active',
            'default_currency', 'timezone', 'language',
            'contact_email', 'contact_phone', 'address',
            'logo', 'description',
            'agencies_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_agencies_count(self, obj):
        return obj.agencies.count()


class TenantListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Tenant list."""
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'is_active', 'default_currency']


class AgencySerializer(serializers.ModelSerializer):
    """Serializer for Agency model."""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    clients_count = serializers.SerializerMethodField()
    cost_centers_count = serializers.SerializerMethodField()

    class Meta:
        model = Agency
        fields = [
            'id', 'tenant', 'tenant_name', 'name', 'code', 'is_active',
            'contact_email', 'contact_phone', 'address',
            'default_currency', 'logo', 'description',
            'clients_count', 'cost_centers_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_clients_count(self, obj):
        return obj.clients.count()

    def get_cost_centers_count(self, obj):
        return obj.cost_centers.count()


class AgencyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Agency list."""
    class Meta:
        model = Agency
        fields = ['id', 'name', 'code', 'is_active']


class CostCenterSerializer(serializers.ModelSerializer):
    """Serializer for CostCenter model."""
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    annual_budget = serializers.DecimalField(
        max_digits=18, decimal_places=2, read_only=True
    )

    class Meta:
        model = CostCenter
        fields = [
            'id', 'agency', 'agency_name', 'name', 'code', 'is_active',
            'description', 'annual_budget_micros', 'annual_budget',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'annual_budget']


class CostCenterListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for CostCenter list."""
    class Meta:
        model = CostCenter
        fields = ['id', 'name', 'code', 'is_active']


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model."""
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    cost_center_name = serializers.CharField(
        source='cost_center.name', read_only=True, allow_null=True
    )
    advertisers_count = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 'agency', 'agency_name', 'cost_center', 'cost_center_name',
            'name', 'code', 'is_active',
            'contact_name', 'contact_email', 'contact_phone', 'address',
            'industry', 'website', 'logo', 'notes',
            'advertisers_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_advertisers_count(self, obj):
        return obj.advertisers.count()


class ClientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Client list."""
    class Meta:
        model = Client
        fields = ['id', 'name', 'code', 'is_active', 'industry']


class AdvertiserSerializer(serializers.ModelSerializer):
    """Serializer for Advertiser model."""
    client_name = serializers.CharField(source='client.name', read_only=True)
    agency_name = serializers.CharField(source='client.agency.name', read_only=True)

    class Meta:
        model = Advertiser
        fields = [
            'id', 'client', 'client_name', 'agency_name',
            'name', 'code', 'is_active',
            'brand_name', 'category',
            'contact_name', 'contact_email',
            'logo', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdvertiserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Advertiser list."""
    class Meta:
        model = Advertiser
        fields = ['id', 'name', 'code', 'is_active', 'brand_name']


class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for Currency model."""
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol', 'is_active', 'decimal_places']


class ExchangeRateSerializer(serializers.ModelSerializer):
    """Serializer for ExchangeRate model."""
    from_currency_code = serializers.CharField(
        source='from_currency.code', read_only=True
    )
    to_currency_code = serializers.CharField(
        source='to_currency.code', read_only=True
    )

    class Meta:
        model = ExchangeRate
        fields = [
            'id', 'from_currency', 'from_currency_code',
            'to_currency', 'to_currency_code',
            'rate', 'effective_date', 'source',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    class Meta:
        model = AuditLog
        fields = [
            'id', 'timestamp', 'user_id', 'user_email', 'action',
            'entity_type', 'entity_id', 'entity_name',
            'old_values', 'new_values', 'ip_address', 'notes'
        ]
        read_only_fields = fields


# =============================================================================
# NESTED SERIALIZERS FOR HIERARCHICAL DATA
# =============================================================================

class AdvertiserNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for Advertiser within Client."""
    class Meta:
        model = Advertiser
        fields = ['id', 'name', 'code', 'brand_name', 'is_active']


class ClientNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for Client within Agency."""
    advertisers = AdvertiserNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'name', 'code', 'is_active', 'advertisers']


class CostCenterNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for CostCenter within Agency."""
    class Meta:
        model = CostCenter
        fields = ['id', 'name', 'code', 'is_active']


class AgencyNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for Agency with clients and cost centers."""
    clients = ClientNestedSerializer(many=True, read_only=True)
    cost_centers = CostCenterNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Agency
        fields = ['id', 'name', 'code', 'is_active', 'clients', 'cost_centers']


class TenantDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Tenant with nested agencies."""
    agencies = AgencyNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'is_active',
            'default_currency', 'timezone', 'language',
            'contact_email', 'contact_phone', 'address',
            'logo', 'description', 'agencies',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
