"""
Core URLs - Multi-tenancy and Business Hierarchy API Routes
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TenantViewSet, AgencyViewSet, CostCenterViewSet,
    ClientViewSet, AdvertiserViewSet,
    CurrencyViewSet, ExchangeRateViewSet, AuditLogViewSet
)

router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'agencies', AgencyViewSet, basename='agency')
router.register(r'cost-centers', CostCenterViewSet, basename='costcenter')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'advertisers', AdvertiserViewSet, basename='advertiser')
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'exchange-rates', ExchangeRateViewSet, basename='exchangerate')
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path('', include(router.urls)),
]
