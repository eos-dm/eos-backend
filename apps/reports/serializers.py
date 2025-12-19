"""
Reports Serializers - Module 6 API
"""
from rest_framework import serializers
from .models import SavedReport, Dashboard, DashboardWidget, ReportExport, Alert, AlertHistory


class SavedReportSerializer(serializers.ModelSerializer):
    """Serializer for SavedReport model."""
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = SavedReport
        fields = [
            'id', 'user', 'user_email',
            'name', 'description', 'report_type',
            'filters', 'columns', 'sorting', 'grouping',
            'is_public', 'shared_with',
            'is_scheduled', 'schedule_frequency', 'schedule_recipients', 'last_sent_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SavedReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for SavedReport list."""

    class Meta:
        model = SavedReport
        fields = [
            'id', 'name', 'report_type', 'is_public', 'is_scheduled',
            'created_at', 'updated_at'
        ]


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for DashboardWidget model."""

    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'dashboard', 'name', 'widget_type',
            'config', 'data_source', 'filters',
            'position_x', 'position_y', 'width', 'height',
            'refresh_interval',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for Dashboard model."""
    widgets = DashboardWidgetSerializer(many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = [
            'id', 'user', 'name', 'description', 'role',
            'layout', 'is_default', 'is_system',
            'widgets',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Dashboard list."""
    widgets_count = serializers.SerializerMethodField()

    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'role', 'is_default', 'is_system',
            'widgets_count', 'created_at'
        ]

    def get_widgets_count(self, obj):
        return obj.widgets.count()


class ReportExportSerializer(serializers.ModelSerializer):
    """Serializer for ReportExport model."""
    user_email = serializers.CharField(source='user.email', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ReportExport
        fields = [
            'id', 'user', 'user_email', 'saved_report',
            'name', 'format', 'status',
            'config', 'file', 'file_url', 'file_size', 'row_count',
            'started_at', 'completed_at', 'error_message', 'expires_at',
            'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'file', 'file_size', 'row_count',
            'started_at', 'completed_at', 'error_message', 'created_at'
        ]

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AlertHistorySerializer(serializers.ModelSerializer):
    """Serializer for AlertHistory model."""
    acknowledged_by_name = serializers.CharField(
        source='acknowledged_by.full_name', read_only=True, allow_null=True
    )

    class Meta:
        model = AlertHistory
        fields = [
            'id', 'alert', 'triggered_at', 'message', 'data',
            'is_acknowledged', 'acknowledged_by', 'acknowledged_by_name', 'acknowledged_at'
        ]
        read_only_fields = ['id', 'triggered_at']


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model."""
    history = AlertHistorySerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'user', 'user_email',
            'name', 'alert_type', 'severity',
            'conditions',
            'notify_email', 'notify_inapp',
            'is_active', 'last_triggered_at',
            'history',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'last_triggered_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AlertListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Alert list."""

    class Meta:
        model = Alert
        fields = [
            'id', 'name', 'alert_type', 'severity',
            'is_active', 'last_triggered_at'
        ]


# =============================================================================
# REPORT DATA SERIALIZERS
# =============================================================================

class CampaignReportSerializer(serializers.Serializer):
    """Serializer for campaign performance report data."""
    campaign_id = serializers.UUIDField()
    campaign_name = serializers.CharField()
    project_name = serializers.CharField()
    client_name = serializers.CharField()
    status = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    budget = serializers.DecimalField(max_digits=18, decimal_places=2)
    spent = serializers.DecimalField(max_digits=18, decimal_places=2)
    remaining = serializers.DecimalField(max_digits=18, decimal_places=2)
    progress_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)


class BudgetReportSerializer(serializers.Serializer):
    """Serializer for budget overview report data."""
    entity_type = serializers.CharField()
    entity_id = serializers.UUIDField()
    entity_name = serializers.CharField()
    total_budget = serializers.DecimalField(max_digits=18, decimal_places=2)
    allocated = serializers.DecimalField(max_digits=18, decimal_places=2)
    spent = serializers.DecimalField(max_digits=18, decimal_places=2)
    remaining = serializers.DecimalField(max_digits=18, decimal_places=2)
    currency = serializers.CharField()


class TeamWorkloadSerializer(serializers.Serializer):
    """Serializer for team workload report data."""
    user_id = serializers.UUIDField()
    user_name = serializers.CharField()
    role = serializers.CharField()
    active_projects = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    pending_approvals = serializers.IntegerField()
    upcoming_deadlines = serializers.IntegerField()


class DashboardDataSerializer(serializers.Serializer):
    """Serializer for dashboard data response."""
    kpis = serializers.DictField()
    charts = serializers.DictField()
    tables = serializers.ListField()
    alerts = serializers.ListField()
