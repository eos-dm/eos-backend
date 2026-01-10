"""
Core Serializers - Multi-tenancy and Business Hierarchy API
Based on EOS Schema V100
"""
from rest_framework import serializers
from .models import (
    Tenant, Agency, CostCenter, Client, Advertiser,
    Currency
)
from apps.audit.models import AuditLog


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model."""
    agencies_count = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'code_prefix', 'is_active',
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
        fields = ['id', 'name', 'code_prefix', 'is_active']


class AgencySerializer(serializers.ModelSerializer):
    """Serializer for Agency model."""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    cost_centers_count = serializers.SerializerMethodField()

    class Meta:
        model = Agency
        fields = [
            'id', 'tenant', 'tenant_name', 'name', 'internal_code', 'is_active',
            'code_subcampaign', 'description',
            'contact_name', 'contact_email', 'contact_phone',
            'address_line1', 'address_line2', 'address_postal_code',
            'address_city_geoname_id', 'address_country_code',
            'timezone',
            'cost_centers_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_cost_centers_count(self, obj):
        return obj.cost_centers.count()


class AgencyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Agency list."""
    class Meta:
        model = Agency
        fields = ['id', 'name', 'internal_code', 'is_active']


class CostCenterSerializer(serializers.ModelSerializer):
    """Serializer for CostCenter model."""
    agency_name = serializers.CharField(source='agency.name', read_only=True)

    class Meta:
        model = CostCenter
        fields = [
            'id', 'agency', 'agency_name', 'name', 'code', 'internal_code', 'is_active',
            'description', 'default_currency', 'timezone',
            'payment_terms_days', 'billing_email', 'legal_entity_name',
            'tax_id', 'tax_country_code',
            'address_line1', 'address_line2', 'address_postal_code',
            'address_city_geoname_id', 'address_country_code',
            'billing_contact_name', 'billing_contact_phone',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CostCenterListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for CostCenter list."""
    agency_name = serializers.CharField(source='agency.name', read_only=True)

    class Meta:
        model = CostCenter
        fields = ['id', 'name', 'code', 'is_active', 'agency_name']


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model."""
    cost_center_name = serializers.CharField(source='cost_center.name', read_only=True)
    agency_name = serializers.CharField(source='cost_center.agency.name', read_only=True)
    advertisers_count = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 'cost_center', 'cost_center_name', 'agency_name',
            'name', 'internal_code', 'is_active', 'status',
            'description', 'external_id',
            'currency_show', 'timezone',
            'contact_name', 'contact_position', 'contact_email', 'contact_email_alt',
            'contact_phone', 'contact_phone_alt',
            'address_line1', 'address_line2', 'address_postal_code', 'address_city_geoname_id',
            'payment_terms_days_override', 'billing_email_override',
            'credit_limit_amount_micros', 'credit_risk_level',
            'advertisers_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_advertisers_count(self, obj):
        return obj.advertisers.count()


class ClientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Client list."""
    cost_center_name = serializers.CharField(source='cost_center.name', read_only=True)
    agency_name = serializers.CharField(source='cost_center.agency.name', read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'name', 'internal_code', 'is_active', 'status', 'cost_center_name', 'agency_name']


class AdvertiserSerializer(serializers.ModelSerializer):
    """Serializer for Advertiser model."""
    client_name = serializers.CharField(source='client.name', read_only=True)
    agency_name = serializers.CharField(source='client.cost_center.agency.name', read_only=True)

    class Meta:
        model = Advertiser
        fields = [
            'id', 'client', 'client_name', 'agency_name',
            'name', 'internal_code', 'is_active', 'status',
            'tax_id', 'industry',
            'contact_name', 'contact_email', 'contact_email_alt',
            'contact_phone', 'contact_phone_alt',
            'address_line1', 'address_line2', 'address_postal_code',
            'address_city_geoname_id', 'address_country_code',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdvertiserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Advertiser list."""
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = Advertiser
        fields = ['id', 'name', 'internal_code', 'is_active', 'status', 'client_name']


class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for Currency model."""
    class Meta:
        model = Currency
        fields = ['code', 'name', 'symbol', 'is_active']


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    created_by_email = serializers.CharField(source='created_by.email', read_only=True, allow_null=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'entity_type', 'entity_id', 'action',
            'description', 'created_by', 'created_by_email',
            'created_at'
        ]
        read_only_fields = fields


# =============================================================================
# NESTED SERIALIZERS FOR HIERARCHICAL DATA
# =============================================================================

class AdvertiserNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for Advertiser within Client."""
    class Meta:
        model = Advertiser
        fields = ['id', 'name', 'internal_code', 'is_active', 'status']


class ClientNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for Client within CostCenter."""
    advertisers = AdvertiserNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'name', 'internal_code', 'is_active', 'status', 'advertisers']


class CostCenterNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for CostCenter within Agency."""
    clients = ClientNestedSerializer(many=True, read_only=True)

    class Meta:
        model = CostCenter
        fields = ['id', 'name', 'code', 'is_active', 'clients']


class AgencyNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for Agency with cost centers."""
    cost_centers = CostCenterNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Agency
        fields = ['id', 'name', 'internal_code', 'is_active', 'cost_centers']


class TenantDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Tenant with nested agencies."""
    agencies = AgencyNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'code_prefix', 'is_active',
            'agencies',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
