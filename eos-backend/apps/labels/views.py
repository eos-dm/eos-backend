"""
Labels Views - Taxonomy API Endpoints
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.db.models import Count

from .models import (
    LabelDefinition, LabelLevel, LabelValue,
    CampaignLabel, MediaPlanLabel, SubcampaignLabel, ProjectLabel
)
from .serializers import (
    LabelDefinitionSerializer, LabelDefinitionListSerializer,
    LabelDefinitionDetailSerializer,
    LabelLevelSerializer, LabelValueSerializer, LabelValueNestedSerializer,
    CampaignLabelSerializer, MediaPlanLabelSerializer,
    SubcampaignLabelSerializer, ProjectLabelSerializer,
    BulkLabelAssignmentSerializer, LabelStatisticsSerializer
)


class LabelDefinitionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing label definitions.

    IMPORTANT: Maximum 20 label definitions per tenant.
    """
    queryset = LabelDefinition.objects.select_related('tenant').prefetch_related('levels', 'values').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['display_order', 'name', 'created_at']
    ordering = ['display_order', 'name']
    filterset_fields = ['tenant', 'data_type', 'applies_to', 'is_active', 'is_required']

    def get_serializer_class(self):
        if self.action == 'list':
            return LabelDefinitionListSerializer
        if self.action == 'retrieve':
            return LabelDefinitionDetailSerializer
        return LabelDefinitionSerializer

    def create(self, request, *args, **kwargs):
        """Create with validation for max labels."""
        tenant_id = request.data.get('tenant')
        max_labels = getattr(settings, 'MAX_LABEL_DEFINITIONS', 20)

        current_count = LabelDefinition.objects.filter(tenant_id=tenant_id).count()
        if current_count >= max_labels:
            return Response(
                {
                    'error': f'Maximum of {max_labels} label definitions allowed per tenant.',
                    'current_count': current_count,
                    'max_allowed': max_labels
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get label statistics for a tenant."""
        tenant_id = request.query_params.get('tenant')
        if not tenant_id:
            return Response(
                {'error': 'tenant parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        max_labels = getattr(settings, 'MAX_LABEL_DEFINITIONS', 20)
        definitions = LabelDefinition.objects.filter(tenant_id=tenant_id)

        stats = {
            'total_definitions': definitions.count(),
            'max_definitions': max_labels,
            'remaining_slots': max_labels - definitions.count(),
            'total_values': LabelValue.objects.filter(
                label_definition__tenant_id=tenant_id
            ).count(),
            'total_assignments': (
                CampaignLabel.objects.filter(
                    label_value__label_definition__tenant_id=tenant_id
                ).count() +
                MediaPlanLabel.objects.filter(
                    label_value__label_definition__tenant_id=tenant_id
                ).count() +
                SubcampaignLabel.objects.filter(
                    label_value__label_definition__tenant_id=tenant_id
                ).count() +
                ProjectLabel.objects.filter(
                    label_value__label_definition__tenant_id=tenant_id
                ).count()
            ),
            'by_entity_type': {
                'campaigns': CampaignLabel.objects.filter(
                    label_value__label_definition__tenant_id=tenant_id
                ).count(),
                'media_plans': MediaPlanLabel.objects.filter(
                    label_value__label_definition__tenant_id=tenant_id
                ).count(),
                'subcampaigns': SubcampaignLabel.objects.filter(
                    label_value__label_definition__tenant_id=tenant_id
                ).count(),
                'projects': ProjectLabel.objects.filter(
                    label_value__label_definition__tenant_id=tenant_id
                ).count(),
            }
        }

        serializer = LabelStatisticsSerializer(stats)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def values_tree(self, request, pk=None):
        """Get hierarchical tree of values for a label definition."""
        label_def = self.get_object()
        root_values = label_def.values.filter(
            parent__isnull=True,
            is_active=True
        ).order_by('display_order', 'name')

        serializer = LabelValueNestedSerializer(root_values, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Reorder label definitions."""
        label_def = self.get_object()
        new_order = request.data.get('display_order')

        if new_order is not None:
            label_def.display_order = new_order
            label_def.save()

        serializer = self.get_serializer(label_def)
        return Response(serializer.data)


class LabelLevelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing label levels.
    """
    queryset = LabelLevel.objects.select_related('label_definition').all()
    serializer_class = LabelLevelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['level_number']
    ordering = ['level_number']
    filterset_fields = ['label_definition', 'is_active']


class LabelValueViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing label values.
    """
    queryset = LabelValue.objects.select_related(
        'label_definition', 'label_level', 'parent'
    ).prefetch_related('children').all()
    serializer_class = LabelValueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['display_order', 'name', 'created_at']
    ordering = ['display_order', 'name']
    filterset_fields = ['label_definition', 'label_level', 'parent', 'is_active']

    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """Get children of a label value."""
        value = self.get_object()
        children = value.children.filter(is_active=True).order_by('display_order', 'name')
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def ancestors(self, request, pk=None):
        """Get all ancestors of a label value."""
        value = self.get_object()
        ancestors = []
        current = value.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        serializer = self.get_serializer(ancestors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search label values across definitions."""
        query = request.query_params.get('q', '')
        tenant_id = request.query_params.get('tenant')

        values = self.queryset.filter(name__icontains=query, is_active=True)
        if tenant_id:
            values = values.filter(label_definition__tenant_id=tenant_id)

        values = values[:50]  # Limit results
        serializer = self.get_serializer(values, many=True)
        return Response(serializer.data)


# =============================================================================
# LABEL ASSIGNMENT VIEWSETS
# =============================================================================

class CampaignLabelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing campaign labels.
    """
    queryset = CampaignLabel.objects.select_related(
        'campaign', 'label_value', 'label_value__label_definition', 'assigned_by'
    ).all()
    serializer_class = CampaignLabelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['campaign', 'label_value', 'label_value__label_definition']

    @action(detail=False, methods=['post'], url_path='bulk-assign/(?P<campaign_id>[^/.]+)')
    def bulk_assign(self, request, campaign_id=None):
        """Bulk assign labels to a campaign."""
        serializer = BulkLabelAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        label_value_ids = serializer.validated_data['label_values']
        created = []

        for value_id in label_value_ids:
            obj, was_created = CampaignLabel.objects.get_or_create(
                campaign_id=campaign_id,
                label_value_id=value_id,
                defaults={'assigned_by': request.user}
            )
            if was_created:
                created.append(obj)

        result_serializer = CampaignLabelSerializer(created, many=True)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], url_path='bulk-remove/(?P<campaign_id>[^/.]+)')
    def bulk_remove(self, request, campaign_id=None):
        """Bulk remove labels from a campaign."""
        label_value_ids = request.data.get('label_values', [])

        deleted, _ = CampaignLabel.objects.filter(
            campaign_id=campaign_id,
            label_value_id__in=label_value_ids
        ).delete()

        return Response({'deleted': deleted})


class MediaPlanLabelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing media plan labels.
    """
    queryset = MediaPlanLabel.objects.select_related(
        'media_plan', 'label_value', 'label_value__label_definition', 'assigned_by'
    ).all()
    serializer_class = MediaPlanLabelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['media_plan', 'label_value', 'label_value__label_definition']


class SubcampaignLabelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing subcampaign labels.
    """
    queryset = SubcampaignLabel.objects.select_related(
        'subcampaign', 'label_value', 'label_value__label_definition', 'assigned_by'
    ).all()
    serializer_class = SubcampaignLabelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['subcampaign', 'label_value', 'label_value__label_definition']


class ProjectLabelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing project labels.
    """
    queryset = ProjectLabel.objects.select_related(
        'project', 'label_value', 'label_value__label_definition', 'assigned_by'
    ).all()
    serializer_class = ProjectLabelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'label_value', 'label_value__label_definition']
