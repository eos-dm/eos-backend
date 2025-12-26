"""
Core Views - Multi-tenancy and Business Hierarchy API Endpoints
Based on EOS Schema V100
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Tenant, Agency, CostCenter, Client, Advertiser,
    Currency
)
from apps.audit.models import AuditLog
from .serializers import (
    TenantSerializer, TenantListSerializer, TenantDetailSerializer,
    AgencySerializer, AgencyListSerializer,
    CostCenterSerializer, CostCenterListSerializer,
    ClientSerializer, ClientListSerializer,
    AdvertiserSerializer, AdvertiserListSerializer,
    CurrencySerializer, AuditLogSerializer
)
from .permissions import IsTenantAdmin, CanAccessAgency


class TenantViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing tenants.
    Only accessible by superadmins.
    """
    queryset = Tenant.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code_prefix']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active']

    def get_serializer_class(self):
        if self.action == 'list':
            return TenantListSerializer
        if self.action == 'retrieve':
            return TenantDetailSerializer
        return TenantSerializer

    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        """Get full hierarchy for a tenant."""
        tenant = self.get_object()
        serializer = TenantDetailSerializer(tenant)
        return Response(serializer.data)


class AgencyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing agencies.
    """
    queryset = Agency.objects.select_related('tenant').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'internal_code', 'contact_email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active', 'tenant']

    def get_serializer_class(self):
        if self.action == 'list':
            return AgencyListSerializer
        return AgencySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by tenant if not superuser
        user = self.request.user
        if not user.is_superuser:
            # Get user's accessible tenants
            if hasattr(user, 'get_accessible_tenant_ids'):
                tenant_ids = user.get_accessible_tenant_ids()
                queryset = queryset.filter(tenant_id__in=tenant_ids)
        return queryset

    @action(detail=True, methods=['get'])
    def cost_centers(self, request, pk=None):
        """Get all cost centers for an agency."""
        agency = self.get_object()
        cost_centers = agency.cost_centers.all()
        serializer = CostCenterListSerializer(cost_centers, many=True)
        return Response(serializer.data)


class CostCenterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing cost centers.
    """
    queryset = CostCenter.objects.select_related('agency', 'agency__tenant').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'internal_code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active', 'agency']

    def get_serializer_class(self):
        if self.action == 'list':
            return CostCenterListSerializer
        return CostCenterSerializer

    @action(detail=True, methods=['get'])
    def clients(self, request, pk=None):
        """Get all clients for a cost center."""
        cost_center = self.get_object()
        clients = cost_center.clients.all()
        serializer = ClientListSerializer(clients, many=True)
        return Response(serializer.data)


class ClientViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing clients.
    """
    queryset = Client.objects.select_related(
        'cost_center', 'cost_center__agency', 'cost_center__agency__tenant'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'internal_code', 'contact_email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active', 'cost_center', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClientListSerializer
        return ClientSerializer

    @action(detail=True, methods=['get'])
    def advertisers(self, request, pk=None):
        """Get all advertisers for a client."""
        client = self.get_object()
        advertisers = client.advertisers.all()
        serializer = AdvertiserListSerializer(advertisers, many=True)
        return Response(serializer.data)


class AdvertiserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing advertisers.
    """
    queryset = Advertiser.objects.select_related(
        'client', 'client__cost_center', 'client__cost_center__agency'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'internal_code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active', 'client', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return AdvertiserListSerializer
        return AdvertiserSerializer


class CurrencyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing currencies.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['code', 'name']
    filterset_fields = ['is_active']


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing audit logs.
    Read-only access to audit trail.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['entity_type', 'action', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    filterset_fields = ['action', 'entity_type']

    @action(detail=False, methods=['get'])
    def by_entity(self, request):
        """Get audit logs for a specific entity."""
        entity_type = request.query_params.get('entity_type')
        entity_id = request.query_params.get('entity_id')

        if not entity_type or not entity_id:
            return Response(
                {'error': 'entity_type and entity_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        logs = self.queryset.filter(
            entity_type=entity_type,
            entity_id=entity_id
        )
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
