"""
Reports URLs - Module 6 API Routes
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SavedReportViewSet, DashboardViewSet, DashboardWidgetViewSet,
    ReportExportViewSet, AlertViewSet, AlertHistoryViewSet,
    DashboardDataView, CampaignReportView, BudgetReportView
)

router = DefaultRouter()
router.register(r'saved', SavedReportViewSet, basename='savedreport')
router.register(r'dashboards', DashboardViewSet, basename='dashboard')
router.register(r'widgets', DashboardWidgetViewSet, basename='dashboardwidget')
router.register(r'exports', ReportExportViewSet, basename='reportexport')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'alert-history', AlertHistoryViewSet, basename='alerthistory')

urlpatterns = [
    path('', include(router.urls)),

    # Dashboard data endpoints
    path('dashboard-data/', DashboardDataView.as_view(), name='dashboard-data'),
    path('dashboard-data/<str:role>/', DashboardDataView.as_view(), name='dashboard-data-role'),

    # Report data endpoints
    path('campaign-report/', CampaignReportView.as_view(), name='campaign-report'),
    path('budget-report/', BudgetReportView.as_view(), name='budget-report'),
]
