"""
Core Views - Multi-tenancy and Business Hierarchy API Endpoints
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Tenant, Agency, CostCenter, Client, Advertiser,
    Currency, ExchangeRate, AuditLog
)
from .serializers import (
    TenantSerializer, TenantListSerializer, TenantDetailSerializer,
    AgencySerializer, AgencyListSerializer,
    CostCenterSerializer, CostCenterListSerializer,
    ClientSerializer, ClientListSerializer,
    AdvertiserSerializer, AdvertiserListSerializer,
    CurrencySerializer, ExchangeRateSerializer, AuditLogSerializer
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
    search_fields = ['name', 'slug', 'contact_email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active', 'default_currency']

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
    search_fields = ['name', 'code', 'contact_email']
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
            tenant_ids = user.get_accessible_tenant_ids()
            queryset = queryset.filter(tenant_id__in=tenant_ids)
        return queryset

    @action(detail=True, methods=['get'])
    def clients(self, request, pk=None):
        """Get all clients for an agency."""
        agency = self.get_object()
        clients = agency.clients.all()
        serializer = ClientListSerializer(clients, many=True)
        return Response(serializer.data)

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
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active', 'agency']

    def get_serializer_class(self):
        if self.action == 'list':
            return CostCenterListSerializer
        return CostCenterSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing clients.
    """
    queryset = Client.objects.select_related(
        'agency', 'agency__tenant', 'cost_center'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'contact_email', 'industry']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active', 'agency', 'industry']

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
        'client', 'client__agency', 'client__agency__tenant'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'brand_name', 'category']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active', 'client', 'category']

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


class ExchangeRateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing exchange rates.
    """
    queryset = ExchangeRate.objects.select_related(
        'from_currency', 'to_currency'
    ).all()
    serializer_class = ExchangeRateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['effective_date']
    ordering = ['-effective_date']
    filterset_fields = ['from_currency', 'to_currency']

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest exchange rates for all currency pairs."""
        from django.db.models import Max

        # Get the latest rate for each currency pair
        latest_dates = ExchangeRate.objects.values(
            'from_currency', 'to_currency'
        ).annotate(latest_date=Max('effective_date'))

        rates = []
        for item in latest_dates:
            rate = ExchangeRate.objects.filter(
                from_currency=item['from_currency'],
                to_currency=item['to_currency'],
                effective_date=item['latest_date']
            ).first()
            if rate:
                rates.append(rate)

        serializer = self.get_serializer(rates, many=True)
        return Response(serializer.data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing audit logs.
    Read-only access to audit trail.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['entity_name', 'user_email']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    filterset_fields = ['action', 'entity_type', 'user_id']

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
