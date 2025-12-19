"""
Campaigns Views - Module 4 API Endpoints
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from django.utils import timezone

from .models import (
    Project, Campaign, MediaPlan, Subcampaign,
    SubcampaignVersion, SubcampaignFee, CampaignComment, CampaignDocument
)
from .serializers import (
    ProjectSerializer, ProjectListSerializer, ProjectDetailSerializer,
    CampaignSerializer, CampaignListSerializer, CampaignDetailSerializer,
    MediaPlanSerializer, MediaPlanListSerializer, MediaPlanDetailSerializer,
    SubcampaignSerializer, SubcampaignListSerializer, SubcampaignDetailSerializer,
    SubcampaignVersionSerializer, SubcampaignFeeSerializer,
    CampaignCommentSerializer, CampaignDocumentSerializer
)
from .filters import ProjectFilter, CampaignFilter, MediaPlanFilter, SubcampaignFilter


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing projects.
    """
    queryset = Project.objects.select_related(
        'advertiser', 'advertiser__client', 'advertiser__client__agency',
        'owner', 'planner'
    ).prefetch_related('campaigns').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at', 'start_date', 'budget_micros']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a project as a template."""
        project = self.get_object()

        new_project = Project.objects.create(
            advertiser=project.advertiser,
            name=f"{project.name} (Copy)",
            code=f"{project.code}_copy",
            description=project.description,
            status='draft',
            budget_micros=project.budget_micros,
            currency=project.currency,
            owner=request.user,
            notes=project.notes
        )

        serializer = ProjectSerializer(new_project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get project statistics."""
        project = self.get_object()

        campaigns = project.campaigns.all()
        stats = {
            'total_campaigns': campaigns.count(),
            'campaigns_by_status': {},
            'total_budget_micros': project.budget_micros,
            'allocated_budget_micros': sum(c.budget_micros for c in campaigns),
            'total_media_plans': sum(c.media_plans.count() for c in campaigns),
        }

        for status_choice in Campaign.STATUS_CHOICES:
            count = campaigns.filter(status=status_choice[0]).count()
            stats['campaigns_by_status'][status_choice[0]] = count

        return Response(stats)

    @action(detail=False, methods=['get'])
    def kanban(self, request):
        """Get projects organized by status for kanban view."""
        projects = self.filter_queryset(self.get_queryset())

        kanban_data = {}
        for status_choice in Project.STATUS_CHOICES:
            status_projects = projects.filter(status=status_choice[0])
            kanban_data[status_choice[0]] = {
                'label': status_choice[1],
                'count': status_projects.count(),
                'projects': ProjectListSerializer(status_projects[:20], many=True).data
            }

        return Response(kanban_data)


class CampaignViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing campaigns.
    """
    queryset = Campaign.objects.select_related(
        'project', 'project__advertiser', 'project__advertiser__client',
        'owner'
    ).prefetch_related('media_plans').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CampaignFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at', 'start_date', 'end_date', 'budget_micros']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return CampaignListSerializer
        if self.action == 'retrieve':
            return CampaignDetailSerializer
        return CampaignSerializer

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a campaign."""
        campaign = self.get_object()

        new_campaign = Campaign.objects.create(
            project=campaign.project,
            name=f"{campaign.name} (Copy)",
            code=f"{campaign.code}_copy",
            description=campaign.description,
            status='draft',
            objective=campaign.objective,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            budget_micros=campaign.budget_micros,
            currency=campaign.currency,
            target_audience=campaign.target_audience,
            target_countries=campaign.target_countries,
            target_kpis=campaign.target_kpis,
            owner=request.user,
            notes=campaign.notes
        )

        serializer = CampaignSerializer(new_campaign)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change campaign status."""
        campaign = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Campaign.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        campaign.status = new_status
        campaign.save()

        serializer = CampaignSerializer(campaign)
        return Response(serializer.data)

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
                'title': campaign.name,
                'start': campaign.start_date.isoformat(),
                'end': campaign.end_date.isoformat(),
                'status': campaign.status,
                'project_id': str(campaign.project.id),
                'project_name': campaign.project.name,
            })

        return Response(data)


class MediaPlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing media plans.
    """
    queryset = MediaPlan.objects.select_related(
        'campaign', 'campaign__project',
        'created_by', 'approved_by', 'client_approved_by'
    ).prefetch_related('subcampaigns').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MediaPlanFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'version']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return MediaPlanListSerializer
        if self.action == 'retrieve':
            return MediaPlanDetailSerializer
        return MediaPlanSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """Create a new version of the media plan."""
        media_plan = self.get_object()
        new_plan = media_plan.create_new_version()
        new_plan.created_by = request.user
        new_plan.save()

        serializer = MediaPlanDetailSerializer(new_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve the media plan (internal approval)."""
        media_plan = self.get_object()

        if media_plan.status not in ['draft', 'pending_internal_review']:
            return Response(
                {'error': 'Media plan cannot be approved in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        media_plan.status = 'internal_approved'
        media_plan.approved_by = request.user
        media_plan.approved_at = timezone.now()
        media_plan.save()

        serializer = MediaPlanSerializer(media_plan)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit_for_client_review(self, request, pk=None):
        """Submit media plan for client review."""
        media_plan = self.get_object()

        if media_plan.status != 'internal_approved':
            return Response(
                {'error': 'Media plan must be internally approved first'},
                status=status.HTTP_400_BAD_REQUEST
            )

        media_plan.status = 'pending_client_review'
        media_plan.save()

        serializer = MediaPlanSerializer(media_plan)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def client_approve(self, request, pk=None):
        """Client approval of media plan."""
        media_plan = self.get_object()

        if media_plan.status != 'pending_client_review':
            return Response(
                {'error': 'Media plan is not pending client review'},
                status=status.HTTP_400_BAD_REQUEST
            )

        media_plan.status = 'client_approved'
        media_plan.client_approved_by = request.user
        media_plan.client_approved_at = timezone.now()
        media_plan.save()

        serializer = MediaPlanSerializer(media_plan)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def compare_versions(self, request, pk=None):
        """Compare two versions of a media plan."""
        media_plan = self.get_object()
        compare_version = request.query_params.get('compare_to')

        if not compare_version:
            return Response(
                {'error': 'compare_to version number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            other_plan = MediaPlan.objects.get(
                campaign=media_plan.campaign,
                version=compare_version
            )
        except MediaPlan.DoesNotExist:
            return Response(
                {'error': 'Version not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        comparison = {
            'current': MediaPlanDetailSerializer(media_plan).data,
            'compare_to': MediaPlanDetailSerializer(other_plan).data,
            'differences': {
                'budget_change': media_plan.total_budget_micros - other_plan.total_budget_micros,
                'subcampaigns_added': [],
                'subcampaigns_removed': [],
                'subcampaigns_modified': [],
            }
        }

        current_codes = set(s.code for s in media_plan.subcampaigns.all())
        other_codes = set(s.code for s in other_plan.subcampaigns.all())

        comparison['differences']['subcampaigns_added'] = list(current_codes - other_codes)
        comparison['differences']['subcampaigns_removed'] = list(other_codes - current_codes)

        return Response(comparison)


class SubcampaignViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing subcampaigns.
    """
    queryset = Subcampaign.objects.select_related(
        'media_plan', 'media_plan__campaign'
    ).prefetch_related('fees', 'versions').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SubcampaignFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at', 'start_date', 'budget_micros']
    ordering = ['channel', 'platform', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return SubcampaignListSerializer
        if self.action == 'retrieve':
            return SubcampaignDetailSerializer
        return SubcampaignSerializer

    def perform_update(self, serializer):
        """Create version snapshot before updating."""
        subcampaign = self.get_object()

        # Create version snapshot
        version_count = subcampaign.versions.count()
        SubcampaignVersion.objects.create(
            subcampaign=subcampaign,
            version_number=version_count + 1,
            budget_micros=subcampaign.budget_micros,
            start_date=subcampaign.start_date,
            end_date=subcampaign.end_date,
            status=subcampaign.status,
            changed_by=self.request.user,
            snapshot_data={
                'name': subcampaign.name,
                'channel': subcampaign.channel,
                'platform': subcampaign.platform,
                'buying_type': subcampaign.buying_type,
            }
        )

        serializer.save()

    @action(detail=True, methods=['post'])
    def calculate_fees(self, request, pk=None):
        """Calculate all fees for the subcampaign."""
        subcampaign = self.get_object()

        for fee in subcampaign.fees.all():
            fee.calculate_fee()

        serializer = SubcampaignDetailSerializer(subcampaign)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get version history of subcampaign."""
        subcampaign = self.get_object()
        versions = subcampaign.versions.all()
        serializer = SubcampaignVersionSerializer(versions, many=True)
        return Response(serializer.data)


class SubcampaignFeeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing subcampaign fees.
    """
    queryset = SubcampaignFee.objects.select_related('subcampaign').all()
    serializer_class = SubcampaignFeeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['subcampaign', 'fee_type', 'calculation_method']

    def perform_create(self, serializer):
        fee = serializer.save()
        fee.calculate_fee()

    def perform_update(self, serializer):
        fee = serializer.save()
        fee.calculate_fee()


class CampaignCommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing campaign comments.
    """
    queryset = CampaignComment.objects.select_related('campaign', 'author', 'parent').all()
    serializer_class = CampaignCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['campaign', 'author', 'is_internal', 'parent']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Filter internal comments for non-staff users
        if user.is_client_portal_user:
            queryset = queryset.filter(is_internal=False)

        return queryset


class CampaignDocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing campaign documents.
    """
    queryset = CampaignDocument.objects.select_related('campaign', 'uploaded_by').all()
    serializer_class = CampaignDocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['campaign', 'document_type', 'is_client_visible']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Filter client-visible documents for portal users
        if user.is_client_portal_user:
            queryset = queryset.filter(is_client_visible=True)

        return queryset
