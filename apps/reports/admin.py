"""
Reports Admin - Module 6 Administration
"""
from django.contrib import admin
from .models import SavedReport, Dashboard, DashboardWidget, ReportExport, Alert, AlertHistory


@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'report_type', 'is_public', 'is_scheduled', 'created_at']
    list_filter = ['report_type', 'is_public', 'is_scheduled']
    search_fields = ['name', 'user__email']
    filter_horizontal = ['shared_with']


class DashboardWidgetInline(admin.TabularInline):
    model = DashboardWidget
    extra = 0


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'role', 'is_default', 'is_system']
    list_filter = ['role', 'is_default', 'is_system']
    search_fields = ['name']
    inlines = [DashboardWidgetInline]


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'dashboard', 'widget_type', 'data_source']
    list_filter = ['widget_type', 'dashboard']


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'format', 'status', 'created_at']
    list_filter = ['format', 'status']
    search_fields = ['name', 'user__email']
    readonly_fields = ['started_at', 'completed_at', 'file_size', 'row_count']


class AlertHistoryInline(admin.TabularInline):
    model = AlertHistory
    extra = 0
    readonly_fields = ['triggered_at', 'is_acknowledged', 'acknowledged_by', 'acknowledged_at']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'alert_type', 'severity', 'is_active', 'last_triggered_at']
    list_filter = ['alert_type', 'severity', 'is_active']
    search_fields = ['name', 'user__email']
    inlines = [AlertHistoryInline]


@admin.register(AlertHistory)
class AlertHistoryAdmin(admin.ModelAdmin):
    list_display = ['alert', 'triggered_at', 'is_acknowledged', 'acknowledged_by']
    list_filter = ['is_acknowledged', 'triggered_at']
    readonly_fields = ['triggered_at']
