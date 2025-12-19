"""
Reports Models - Module 6: Reporting and Role-based Dashboards
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
import uuid


class SavedReport(BaseModel):
    """
    Saved Report - User-saved report configurations.
    """
    REPORT_TYPE_CHOICES = [
        ('campaign_performance', _('Campaign Performance')),
        ('budget_overview', _('Budget Overview')),
        ('media_plan_summary', _('Media Plan Summary')),
        ('project_status', _('Project Status')),
        ('team_workload', _('Team Workload')),
        ('client_overview', _('Client Overview')),
        ('custom', _('Custom Report')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_reports',
        verbose_name=_('user')
    )

    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    report_type = models.CharField(
        _('report type'),
        max_length=30,
        choices=REPORT_TYPE_CHOICES
    )

    # Configuration
    filters = models.JSONField(
        _('filters'),
        default=dict,
        blank=True,
        help_text=_('Report filter configuration')
    )
    columns = models.JSONField(
        _('columns'),
        default=list,
        blank=True,
        help_text=_('Selected columns for the report')
    )
    sorting = models.JSONField(
        _('sorting'),
        default=list,
        blank=True
    )
    grouping = models.JSONField(
        _('grouping'),
        default=list,
        blank=True
    )

    # Sharing
    is_public = models.BooleanField(_('is public'), default=False)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='shared_reports',
        verbose_name=_('shared with'),
        blank=True
    )

    # Scheduling
    is_scheduled = models.BooleanField(_('is scheduled'), default=False)
    schedule_frequency = models.CharField(
        _('schedule frequency'),
        max_length=20,
        blank=True,
        help_text=_('daily, weekly, monthly')
    )
    schedule_recipients = models.JSONField(
        _('schedule recipients'),
        default=list,
        blank=True
    )
    last_sent_at = models.DateTimeField(_('last sent at'), null=True, blank=True)

    class Meta:
        verbose_name = _('saved report')
        verbose_name_plural = _('saved reports')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.user.email})"


class Dashboard(BaseModel):
    """
    Dashboard - Customizable dashboard with widgets.
    """
    ROLE_CHOICES = [
        ('planner', _('Planner')),
        ('operations', _('Operations')),
        ('finance', _('Finance')),
        ('accounts', _('Accounts')),
        ('admin', _('Admin')),
        ('client', _('Client')),
        ('custom', _('Custom')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboards',
        verbose_name=_('user'),
        null=True,
        blank=True
    )

    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='custom'
    )

    # Layout
    layout = models.JSONField(
        _('layout'),
        default=list,
        help_text=_('Dashboard layout configuration')
    )

    is_default = models.BooleanField(_('is default'), default=False)
    is_system = models.BooleanField(
        _('is system'),
        default=False,
        help_text=_('System dashboards cannot be deleted')
    )

    class Meta:
        verbose_name = _('dashboard')
        verbose_name_plural = _('dashboards')
        ordering = ['role', 'name']

    def __str__(self):
        return f"{self.name} ({self.role})"


class DashboardWidget(BaseModel):
    """
    Dashboard Widget - Individual widget on a dashboard.
    """
    WIDGET_TYPE_CHOICES = [
        ('kpi_card', _('KPI Card')),
        ('chart_line', _('Line Chart')),
        ('chart_bar', _('Bar Chart')),
        ('chart_pie', _('Pie Chart')),
        ('table', _('Table')),
        ('list', _('List')),
        ('calendar', _('Calendar')),
        ('progress', _('Progress Bar')),
        ('alerts', _('Alerts')),
        ('tasks', _('Tasks')),
    ]

    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets',
        verbose_name=_('dashboard')
    )

    name = models.CharField(_('name'), max_length=255)
    widget_type = models.CharField(
        _('widget type'),
        max_length=20,
        choices=WIDGET_TYPE_CHOICES
    )

    # Configuration
    config = models.JSONField(
        _('config'),
        default=dict,
        help_text=_('Widget configuration')
    )
    data_source = models.CharField(
        _('data source'),
        max_length=100,
        help_text=_('API endpoint or data source identifier')
    )
    filters = models.JSONField(
        _('filters'),
        default=dict,
        blank=True
    )

    # Position
    position_x = models.PositiveSmallIntegerField(_('position X'), default=0)
    position_y = models.PositiveSmallIntegerField(_('position Y'), default=0)
    width = models.PositiveSmallIntegerField(_('width'), default=4)
    height = models.PositiveSmallIntegerField(_('height'), default=3)

    # Refresh
    refresh_interval = models.PositiveIntegerField(
        _('refresh interval'),
        default=0,
        help_text=_('Refresh interval in seconds (0 = no auto refresh)')
    )

    class Meta:
        verbose_name = _('dashboard widget')
        verbose_name_plural = _('dashboard widgets')
        ordering = ['position_y', 'position_x']

    def __str__(self):
        return f"{self.name} ({self.widget_type})"


class ReportExport(BaseModel):
    """
    Report Export - Track exported reports.
    """
    FORMAT_CHOICES = [
        ('xlsx', _('Excel')),
        ('csv', _('CSV')),
        ('pdf', _('PDF')),
    ]

    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_exports',
        verbose_name=_('user')
    )
    saved_report = models.ForeignKey(
        SavedReport,
        on_delete=models.SET_NULL,
        related_name='exports',
        verbose_name=_('saved report'),
        null=True,
        blank=True
    )

    name = models.CharField(_('name'), max_length=255)
    format = models.CharField(
        _('format'),
        max_length=10,
        choices=FORMAT_CHOICES
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Configuration used
    config = models.JSONField(
        _('config'),
        default=dict
    )

    # Result
    file = models.FileField(
        _('file'),
        upload_to='report_exports/',
        blank=True,
        null=True
    )
    file_size = models.PositiveIntegerField(_('file size'), default=0)
    row_count = models.PositiveIntegerField(_('row count'), default=0)

    # Processing
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    error_message = models.TextField(_('error message'), blank=True)

    # Expiration
    expires_at = models.DateTimeField(_('expires at'), null=True, blank=True)

    class Meta:
        verbose_name = _('report export')
        verbose_name_plural = _('report exports')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.format})"


class Alert(BaseModel):
    """
    Alert - Configurable alerts and notifications.
    """
    ALERT_TYPE_CHOICES = [
        ('budget_threshold', _('Budget Threshold')),
        ('campaign_ending', _('Campaign Ending')),
        ('approval_pending', _('Approval Pending')),
        ('performance_drop', _('Performance Drop')),
        ('deadline_approaching', _('Deadline Approaching')),
        ('custom', _('Custom')),
    ]

    SEVERITY_CHOICES = [
        ('info', _('Info')),
        ('warning', _('Warning')),
        ('critical', _('Critical')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name=_('user')
    )

    name = models.CharField(_('name'), max_length=255)
    alert_type = models.CharField(
        _('alert type'),
        max_length=30,
        choices=ALERT_TYPE_CHOICES
    )
    severity = models.CharField(
        _('severity'),
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='info'
    )

    # Conditions
    conditions = models.JSONField(
        _('conditions'),
        default=dict,
        help_text=_('Alert trigger conditions')
    )

    # Actions
    notify_email = models.BooleanField(_('notify email'), default=True)
    notify_inapp = models.BooleanField(_('notify in-app'), default=True)

    is_active = models.BooleanField(_('is active'), default=True)
    last_triggered_at = models.DateTimeField(_('last triggered at'), null=True, blank=True)

    class Meta:
        verbose_name = _('alert')
        verbose_name_plural = _('alerts')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.alert_type})"


class AlertHistory(BaseModel):
    """
    Alert History - Record of triggered alerts.
    """
    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('alert')
    )

    triggered_at = models.DateTimeField(_('triggered at'), auto_now_add=True)
    message = models.TextField(_('message'))
    data = models.JSONField(_('data'), default=dict)

    is_acknowledged = models.BooleanField(_('is acknowledged'), default=False)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='acknowledged_alerts',
        verbose_name=_('acknowledged by'),
        null=True,
        blank=True
    )
    acknowledged_at = models.DateTimeField(_('acknowledged at'), null=True, blank=True)

    class Meta:
        verbose_name = _('alert history')
        verbose_name_plural = _('alert histories')
        ordering = ['-triggered_at']

    def __str__(self):
        return f"{self.alert.name} - {self.triggered_at}"
