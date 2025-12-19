"""
Campaigns Filters - Advanced filtering for Module 4
"""
import django_filters
from .models import Project, Campaign, MediaPlan, Subcampaign


class ProjectFilter(django_filters.FilterSet):
    """Filter for Project model."""
    advertiser = django_filters.UUIDFilter(field_name='advertiser__id')
    client = django_filters.UUIDFilter(field_name='advertiser__client__id')
    agency = django_filters.UUIDFilter(field_name='advertiser__client__agency__id')

    status = django_filters.MultipleChoiceFilter(choices=Project.STATUS_CHOICES)

    start_date_from = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_from = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')

    budget_min = django_filters.NumberFilter(field_name='budget_micros', lookup_expr='gte')
    budget_max = django_filters.NumberFilter(field_name='budget_micros', lookup_expr='lte')

    owner = django_filters.UUIDFilter(field_name='owner__id')
    planner = django_filters.UUIDFilter(field_name='planner__id')

    is_template = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter(field_name='status', method='filter_is_active')

    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Project
        fields = [
            'advertiser', 'client', 'agency', 'status',
            'start_date_from', 'start_date_to', 'end_date_from', 'end_date_to',
            'budget_min', 'budget_max', 'owner', 'planner', 'is_template',
            'currency'
        ]

    def filter_is_active(self, queryset, name, value):
        if value:
            return queryset.filter(status='active')
        return queryset.exclude(status='active')


class CampaignFilter(django_filters.FilterSet):
    """Filter for Campaign model."""
    project = django_filters.UUIDFilter(field_name='project__id')
    advertiser = django_filters.UUIDFilter(field_name='project__advertiser__id')
    client = django_filters.UUIDFilter(field_name='project__advertiser__client__id')
    agency = django_filters.UUIDFilter(field_name='project__advertiser__client__agency__id')

    status = django_filters.MultipleChoiceFilter(choices=Campaign.STATUS_CHOICES)
    objective = django_filters.MultipleChoiceFilter(choices=Campaign.OBJECTIVE_CHOICES)

    start_date_from = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_from = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')

    # Active campaigns (currently running)
    active_on = django_filters.DateFilter(method='filter_active_on')

    budget_min = django_filters.NumberFilter(field_name='budget_micros', lookup_expr='gte')
    budget_max = django_filters.NumberFilter(field_name='budget_micros', lookup_expr='lte')

    owner = django_filters.UUIDFilter(field_name='owner__id')
    is_template = django_filters.BooleanFilter()

    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Campaign
        fields = [
            'project', 'advertiser', 'client', 'agency',
            'status', 'objective',
            'start_date_from', 'start_date_to', 'end_date_from', 'end_date_to',
            'budget_min', 'budget_max', 'owner', 'is_template',
            'currency'
        ]

    def filter_active_on(self, queryset, name, value):
        """Filter campaigns that are active on a specific date."""
        return queryset.filter(
            start_date__lte=value,
            end_date__gte=value,
            status__in=['active', 'approved']
        )


class MediaPlanFilter(django_filters.FilterSet):
    """Filter for MediaPlan model."""
    campaign = django_filters.UUIDFilter(field_name='campaign__id')
    project = django_filters.UUIDFilter(field_name='campaign__project__id')

    status = django_filters.MultipleChoiceFilter(choices=MediaPlan.STATUS_CHOICES)
    is_active_version = django_filters.BooleanFilter()

    version_min = django_filters.NumberFilter(field_name='version', lookup_expr='gte')
    version_max = django_filters.NumberFilter(field_name='version', lookup_expr='lte')

    budget_min = django_filters.NumberFilter(field_name='total_budget_micros', lookup_expr='gte')
    budget_max = django_filters.NumberFilter(field_name='total_budget_micros', lookup_expr='lte')

    created_by = django_filters.UUIDFilter(field_name='created_by__id')
    approved_by = django_filters.UUIDFilter(field_name='approved_by__id')

    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = MediaPlan
        fields = [
            'campaign', 'project', 'status', 'is_active_version',
            'version_min', 'version_max', 'budget_min', 'budget_max',
            'created_by', 'approved_by', 'currency'
        ]


class SubcampaignFilter(django_filters.FilterSet):
    """Filter for Subcampaign model."""
    media_plan = django_filters.UUIDFilter(field_name='media_plan__id')
    campaign = django_filters.UUIDFilter(field_name='media_plan__campaign__id')
    project = django_filters.UUIDFilter(field_name='media_plan__campaign__project__id')

    status = django_filters.MultipleChoiceFilter(choices=Subcampaign.STATUS_CHOICES)
    channel = django_filters.MultipleChoiceFilter(choices=Subcampaign.CHANNEL_CHOICES)
    platform = django_filters.MultipleChoiceFilter(choices=Subcampaign.PLATFORM_CHOICES)
    buying_type = django_filters.MultipleChoiceFilter(choices=Subcampaign.BUYING_TYPE_CHOICES)

    start_date_from = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_from = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')

    budget_min = django_filters.NumberFilter(field_name='budget_micros', lookup_expr='gte')
    budget_max = django_filters.NumberFilter(field_name='budget_micros', lookup_expr='lte')

    has_external_id = django_filters.BooleanFilter(method='filter_has_external_id')

    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Subcampaign
        fields = [
            'media_plan', 'campaign', 'project',
            'status', 'channel', 'platform', 'buying_type',
            'start_date_from', 'start_date_to', 'end_date_from', 'end_date_to',
            'budget_min', 'budget_max', 'currency'
        ]

    def filter_has_external_id(self, queryset, name, value):
        if value:
            return queryset.exclude(external_id='')
        return queryset.filter(external_id='')
