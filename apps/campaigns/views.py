"""
Campaigns Views - Module 4 API Endpoints
Based on EOS Schema V100
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Project, MediaPlan, Campaign, Subcampaign, SubcampaignVersion
)
from .serializers import (
    ProjectSerializer, ProjectListSerializer, ProjectDetailSerializer,
    MediaPlanSerializer, MediaPlanListSerializer, MediaPlanDetailSerializer,
    CampaignSerializer, CampaignListSerializer, CampaignDetailSerializer,
    SubcampaignSerializer, SubcampaignListSerializer, SubcampaignDetailSerializer,
    SubcampaignVersionSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing projects.
    """
    queryset = Project.objects.select_related(
        'advertiser', 'advertiser__client', 'advertiser__client__cost_center'
    ).prefetch_related('media_plans').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'internal_code', 'description']
    ordering_fields = ['name', 'created_at', 'status']
    ordering = ['-created_at']
    filterset_fields = ['is_active', 'status', 'advertiser']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get project statistics."""
        project = self.get_object()
        media_plans = project.media_plans.all()

        total_campaigns = 0
        total_subcampaigns = 0
        total_budget_micros = 0

        for mp in media_plans:
            campaigns = mp.campaigns.all()
            total_campaigns += campaigns.count()
            for c in campaigns:
                total_subcampaigns += c.subcampaigns.count()
            total_budget_micros += mp.total_budget_micros or 0

        stats = {
            'total_media_plans': media_plans.count(),
            'total_campaigns': total_campaigns,
            'total_subcampaigns': total_subcampaigns,
            'total_budget_micros': total_budget_micros,
            'total_budget': total_budget_micros / 1_000_000,
        }

        return Response(stats)


class MediaPlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing media plans.
    """
    queryset = MediaPlan.objects.select_related(
        'project', 'project__advertiser'
    ).prefetch_related('campaigns').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'notes']
    ordering_fields = ['name', 'created_at', 'start_date']
    ordering = ['-created_at']
    filterset_fields = ['is_active', 'status', 'project']

    def get_serializer_class(self):
        if self.action == 'list':
            return MediaPlanListSerializer
        if self.action == 'retrieve':
            return MediaPlanDetailSerializer
        return MediaPlanSerializer

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get media plan statistics."""
        media_plan = self.get_object()
        campaigns = media_plan.campaigns.all()

        total_subcampaigns = 0
        for c in campaigns:
            total_subcampaigns += c.subcampaigns.count()

        stats = {
            'total_campaigns': campaigns.count(),
            'total_subcampaigns': total_subcampaigns,
            'total_budget_micros': media_plan.total_budget_micros or 0,
            'total_budget': (media_plan.total_budget_micros or 0) / 1_000_000,
        }

        return Response(stats)


class CampaignViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing campaigns.
    """
    queryset = Campaign.objects.select_related(
        'media_plan', 'media_plan__project'
    ).prefetch_related('subcampaigns').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['campaign_name', 'internal_campaign_name', 'external_id']
    ordering_fields = ['campaign_name', 'created_at', 'start_date', 'end_date']
    ordering = ['-created_at']
    filterset_fields = ['is_active', 'media_plan', 'category', 'product']

    def get_serializer_class(self):
        if self.action == 'list':
            return CampaignListSerializer
        if self.action == 'retrieve':
            return CampaignDetailSerializer
        return CampaignSerializer

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Get campaigns for calendar view."""
        campaigns = self.filter_queryset(self.get_queryset())

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            campaigns = campaigns.filter(end_date__gte=start_date)
        if end_date:
            campaigns = campaigns.filter(start_date__lte=end_date)

        data = []
        for campaign in campaigns:
            data.append({
                'id': str(campaign.id),
                'title': campaign.campaign_name,
                'start': campaign.start_date.isoformat() if campaign.start_date else None,
                'end': campaign.end_date.isoformat() if campaign.end_date else None,
                'media_plan_id': str(campaign.media_plan.id),
                'media_plan_name': campaign.media_plan.name,
            })

        return Response(data)


class SubcampaignViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing subcampaigns.
    """
    queryset = Subcampaign.objects.select_related(
        'campaign', 'campaign__media_plan'
    ).prefetch_related('versions').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'subcampaign_code', 'objective']
    ordering_fields = ['name', 'created_at', 'status']
    ordering = ['name']
    filterset_fields = ['is_active', 'status', 'campaign', 'goal', 'publisher']

    def get_serializer_class(self):
        if self.action == 'list':
            return SubcampaignListSerializer
        if self.action == 'retrieve':
            return SubcampaignDetailSerializer
        return SubcampaignSerializer

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change subcampaign status (workflow transition)."""
        subcampaign = self.get_object()
        new_status = request.data.get('status')

        # Validate the status
        from .models import SubcampaignStatusEnum
        valid_statuses = [e.value for e in SubcampaignStatusEnum]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if transition is allowed
        if not subcampaign.is_editable and new_status in ['DRAFT', 'PENDING_INTERNAL']:
            return Response(
                {'error': 'Cannot change status of a non-editable subcampaign back to editable state'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subcampaign.status = new_status
        subcampaign.save()

        serializer = SubcampaignSerializer(subcampaign)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get version history of subcampaign."""
        subcampaign = self.get_object()
        versions = subcampaign.versions.all()
        serializer = SubcampaignVersionSerializer(versions, many=True)
        return Response(serializer.data)


class SubcampaignVersionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing subcampaign versions.
    """
    queryset = SubcampaignVersion.objects.select_related('subcampaign').all()
    serializer_class = SubcampaignVersionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['version_number', 'created_at']
    ordering = ['-version_number']
    filterset_fields = ['subcampaign', 'status', 'is_active']
