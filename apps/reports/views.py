"""
Reports Views - Module 6 API Endpoints
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import SavedReport, Dashboard, DashboardWidget, ReportExport, Alert, AlertHistory
from .serializers import (
    SavedReportSerializer, SavedReportListSerializer,
    DashboardSerializer, DashboardListSerializer, DashboardWidgetSerializer,
    ReportExportSerializer, AlertSerializer, AlertListSerializer, AlertHistorySerializer,
    CampaignReportSerializer, BudgetReportSerializer, TeamWorkloadSerializer,
    DashboardDataSerializer
)


class SavedReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing saved reports.
    """
    queryset = SavedReport.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    filterset_fields = ['report_type', 'is_public', 'is_scheduled']

    def get_serializer_class(self):
        if self.action == 'list':
            return SavedReportListSerializer
        return SavedReportSerializer

    def get_queryset(self):
        """Filter to show user's reports and shared/public reports."""
        user = self.request.user
        return self.queryset.filter(
            Q(user=user) |
            Q(is_public=True) |
            Q(shared_with=user)
        ).distinct()

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a saved report."""
        report = self.get_object()

        new_report = SavedReport.objects.create(
            user=request.user,
            name=f"{report.name} (Copy)",
            description=report.description,
            report_type=report.report_type,
            filters=report.filters,
            columns=report.columns,
            sorting=report.sorting,
            grouping=report.grouping
        )

        serializer = SavedReportSerializer(new_report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Export a saved report."""
        report = self.get_object()
        export_format = request.data.get('format', 'xlsx')

        export = ReportExport.objects.create(
            user=request.user,
            saved_report=report,
            name=f"{report.name} - {timezone.now().strftime('%Y%m%d_%H%M%S')}",
            format=export_format,
            config={
                'filters': report.filters,
                'columns': report.columns,
                'sorting': report.sorting,
                'grouping': report.grouping
            }
        )

        # TODO: Trigger async export task
        # export_report_task.delay(export.id)

        serializer = ReportExportSerializer(export)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class DashboardViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing dashboards.
    """
    queryset = Dashboard.objects.prefetch_related('widgets').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['role', 'is_default']

    def get_serializer_class(self):
        if self.action == 'list':
            return DashboardListSerializer
        return DashboardSerializer

    def get_queryset(self):
        """Filter dashboards for current user."""
        user = self.request.user
        return self.queryset.filter(
            Q(user=user) |
            Q(user__isnull=True, is_system=True)
        )

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this dashboard as default for user."""
        dashboard = self.get_object()

        # Unset other defaults
        Dashboard.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)

        dashboard.is_default = True
        dashboard.user = request.user
        dashboard.save()

        serializer = self.get_serializer(dashboard)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a dashboard."""
        dashboard = self.get_object()

        new_dashboard = Dashboard.objects.create(
            user=request.user,
            name=f"{dashboard.name} (Copy)",
            description=dashboard.description,
            role='custom',
            layout=dashboard.layout,
            is_default=False,
            is_system=False
        )

        # Copy widgets
        for widget in dashboard.widgets.all():
            DashboardWidget.objects.create(
                dashboard=new_dashboard,
                name=widget.name,
                widget_type=widget.widget_type,
                config=widget.config,
                data_source=widget.data_source,
                filters=widget.filters,
                position_x=widget.position_x,
                position_y=widget.position_y,
                width=widget.width,
                height=widget.height,
                refresh_interval=widget.refresh_interval
            )

        serializer = DashboardSerializer(new_dashboard)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing dashboard widgets.
    """
    queryset = DashboardWidget.objects.select_related('dashboard').all()
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dashboard', 'widget_type']

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get data for a specific widget."""
        widget = self.get_object()
        # TODO: Implement data fetching based on widget.data_source
        return Response({
            'widget_id': str(widget.id),
            'data_source': widget.data_source,
            'data': {},  # Placeholder
            'updated_at': timezone.now().isoformat()
        })


class ReportExportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing report exports.
    """
    queryset = ReportExport.objects.select_related('user', 'saved_report').all()
    serializer_class = ReportExportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering = ['-created_at']
    filterset_fields = ['format', 'status']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Get download URL for export."""
        export = self.get_object()

        if export.status != 'completed':
            return Response(
                {'error': 'Export is not ready'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not export.file:
            return Response(
                {'error': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'url': request.build_absolute_uri(export.file.url),
            'filename': export.name,
            'format': export.format,
            'size': export.file_size
        })


class AlertViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing alerts.
    """
    queryset = Alert.objects.prefetch_related('history').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']
    filterset_fields = ['alert_type', 'severity', 'is_active']

    def get_serializer_class(self):
        if self.action == 'list':
            return AlertListSerializer
        return AlertSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle alert active status."""
        alert = self.get_object()
        alert.is_active = not alert.is_active
        alert.save()

        serializer = self.get_serializer(alert)
        return Response(serializer.data)


class AlertHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing alert history.
    """
    queryset = AlertHistory.objects.select_related('alert', 'acknowledged_by').all()
    serializer_class = AlertHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering = ['-triggered_at']
    filterset_fields = ['alert', 'is_acknowledged']

    def get_queryset(self):
        return self.queryset.filter(alert__user=self.request.user)

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert."""
        history = self.get_object()

        if history.is_acknowledged:
            return Response(
                {'error': 'Alert already acknowledged'},
                status=status.HTTP_400_BAD_REQUEST
            )

        history.is_acknowledged = True
        history.acknowledged_by = request.user
        history.acknowledged_at = timezone.now()
        history.save()

        serializer = self.get_serializer(history)
        return Response(serializer.data)


# =============================================================================
# DASHBOARD DATA VIEWS
# =============================================================================

class DashboardDataView(APIView):
    """
    API endpoint for dashboard data by role.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, role=None):
        """Get dashboard data for a specific role."""
        user = request.user
        role = role or user.role

        data = {
            'kpis': self._get_kpis(user, role),
            'charts': self._get_charts(user, role),
            'tables': self._get_tables(user, role),
            'alerts': self._get_alerts(user)
        }

        return Response(data)

    def _get_kpis(self, user, role):
        """Get KPIs based on role."""
        from apps.campaigns.models import Campaign, Project, MediaPlan

        today = timezone.now().date()

        kpis = {
            'active_campaigns': Campaign.objects.filter(
                status='active'
            ).count(),
            'pending_approvals': 0,  # TODO: Calculate from workflows
            'total_budget': 0,
            'spent_budget': 0,
        }

        if role == 'planner':
            kpis['my_campaigns'] = Campaign.objects.filter(
                owner=user, status__in=['active', 'draft', 'approved']
            ).count()
            kpis['upcoming_deadlines'] = Campaign.objects.filter(
                owner=user,
                end_date__gte=today,
                end_date__lte=today + timedelta(days=7)
            ).count()

        elif role == 'finance':
            budget_data = Project.objects.aggregate(
                total=Sum('budget_micros')
            )
            kpis['total_budget'] = (budget_data['total'] or 0) / 1_000_000

        return kpis

    def _get_charts(self, user, role):
        """Get chart data based on role."""
        return {
            'campaign_status': [],  # TODO: Implement
            'budget_by_client': [],  # TODO: Implement
            'monthly_trend': [],  # TODO: Implement
        }

    def _get_tables(self, user, role):
        """Get table data based on role."""
        return []

    def _get_alerts(self, user):
        """Get recent alerts for user."""
        alerts = AlertHistory.objects.filter(
            alert__user=user,
            is_acknowledged=False
        ).order_by('-triggered_at')[:5]

        return AlertHistorySerializer(alerts, many=True).data


class CampaignReportView(APIView):
    """
    API endpoint for campaign performance report.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get campaign performance report data."""
        from apps.campaigns.models import Campaign

        campaigns = Campaign.objects.select_related(
            'project', 'project__advertiser', 'project__advertiser__client'
        ).all()

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            campaigns = campaigns.filter(status=status_filter)

        client_filter = request.query_params.get('client')
        if client_filter:
            campaigns = campaigns.filter(project__advertiser__client_id=client_filter)

        start_date = request.query_params.get('start_date')
        if start_date:
            campaigns = campaigns.filter(start_date__gte=start_date)

        end_date = request.query_params.get('end_date')
        if end_date:
            campaigns = campaigns.filter(end_date__lte=end_date)

        data = []
        for campaign in campaigns[:100]:
            budget = campaign.budget_micros / 1_000_000
            spent = 0  # TODO: Calculate from actual spend data
            data.append({
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'project_name': campaign.project.name,
                'client_name': campaign.project.advertiser.client.name,
                'status': campaign.status,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'budget': budget,
                'spent': spent,
                'remaining': budget - spent,
                'progress_percentage': (spent / budget * 100) if budget > 0 else 0
            })

        serializer = CampaignReportSerializer(data, many=True)
        return Response(serializer.data)


class BudgetReportView(APIView):
    """
    API endpoint for budget overview report.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get budget overview report data."""
        from apps.core.models import Client
        from apps.campaigns.models import Project

        level = request.query_params.get('level', 'client')

        data = []

        if level == 'client':
            clients = Client.objects.select_related('agency').prefetch_related(
                'advertisers__projects'
            ).all()

            for client in clients:
                total_budget = sum(
                    p.budget_micros for adv in client.advertisers.all()
                    for p in adv.projects.all()
                ) / 1_000_000

                data.append({
                    'entity_type': 'client',
                    'entity_id': client.id,
                    'entity_name': client.name,
                    'total_budget': total_budget,
                    'allocated': total_budget,  # TODO: Calculate properly
                    'spent': 0,  # TODO: Calculate from actual spend
                    'remaining': total_budget,
                    'currency': 'EUR'
                })

        elif level == 'project':
            projects = Project.objects.select_related(
                'advertiser', 'advertiser__client'
            ).all()

            for project in projects:
                budget = project.budget_micros / 1_000_000
                data.append({
                    'entity_type': 'project',
                    'entity_id': project.id,
                    'entity_name': project.name,
                    'total_budget': budget,
                    'allocated': project.total_campaign_budget_micros / 1_000_000,
                    'spent': 0,
                    'remaining': budget,
                    'currency': project.currency
                })

        serializer = BudgetReportSerializer(data, many=True)
        return Response(serializer.data)
