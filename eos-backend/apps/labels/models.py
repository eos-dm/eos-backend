"""
Labels Models - Taxonomy and Label Management System
Based on CHARLI v21 Schema

IMPORTANT: Maximum of 20 Label Definitions allowed per tenant.
Labels support hierarchical structure through Label Levels.
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
import uuid


class LabelDefinition(BaseModel):
    """
    Label Definition - Defines a type of label (e.g., "Region", "Product Type", "Target Audience").

    CONSTRAINT: Maximum 20 label definitions per tenant.
    """
    APPLIES_TO_CHOICES = [
        ('campaign', _('Campaign')),
        ('media_plan', _('Media Plan')),
        ('subcampaign', _('Subcampaign')),
        ('project', _('Project')),
        ('all', _('All Entities')),
    ]

    DATA_TYPE_CHOICES = [
        ('single_select', _('Single Select')),
        ('multi_select', _('Multi Select')),
        ('hierarchical', _('Hierarchical')),
    ]

    tenant = models.ForeignKey(
        'core.Tenant',
        on_delete=models.CASCADE,
        related_name='label_definitions',
        verbose_name=_('tenant')
    )

    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=50)
    description = models.TextField(_('description'), blank=True)

    # Configuration
    data_type = models.CharField(
        _('data type'),
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        default='single_select'
    )
    applies_to = models.CharField(
        _('applies to'),
        max_length=20,
        choices=APPLIES_TO_CHOICES,
        default='all'
    )

    # Display order
    display_order = models.PositiveIntegerField(_('display order'), default=0)

    # Constraints
    is_required = models.BooleanField(_('is required'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)

    # Metadata
    color = models.CharField(_('color'), max_length=7, default='#6B7280')  # Hex color
    icon = models.CharField(_('icon'), max_length=50, blank=True)

    class Meta:
        verbose_name = _('label definition')
        verbose_name_plural = _('label definitions')
        ordering = ['display_order', 'name']
        unique_together = [['tenant', 'code']]
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['applies_to']),
        ]

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"

    def clean(self):
        """Validate maximum 20 label definitions per tenant."""
        if not self.pk:  # Only check on creation
            current_count = LabelDefinition.objects.filter(
                tenant=self.tenant
            ).count()

            max_labels = getattr(settings, 'MAX_LABEL_DEFINITIONS', 20)

            if current_count >= max_labels:
                raise ValidationError(
                    _('Maximum of %(max)s label definitions allowed per tenant.'),
                    params={'max': max_labels}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class LabelLevel(BaseModel):
    """
    Label Level - Defines hierarchy levels within a label definition.

    Example: For "Region" label:
    - Level 1: Continent
    - Level 2: Country
    - Level 3: City
    """
    label_definition = models.ForeignKey(
        LabelDefinition,
        on_delete=models.CASCADE,
        related_name='levels',
        verbose_name=_('label definition')
    )

    name = models.CharField(_('name'), max_length=100)
    level_number = models.PositiveSmallIntegerField(_('level number'))
    description = models.TextField(_('description'), blank=True)

    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('label level')
        verbose_name_plural = _('label levels')
        ordering = ['label_definition', 'level_number']
        unique_together = [['label_definition', 'level_number']]

    def __str__(self):
        return f"{self.label_definition.name} - Level {self.level_number}: {self.name}"


class LabelValue(BaseModel):
    """
    Label Value - Actual values that can be assigned to entities.

    Supports hierarchical structure through parent relationship.
    """
    label_definition = models.ForeignKey(
        LabelDefinition,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name=_('label definition')
    )
    label_level = models.ForeignKey(
        LabelLevel,
        on_delete=models.SET_NULL,
        related_name='values',
        verbose_name=_('label level'),
        null=True,
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name=_('parent'),
        null=True,
        blank=True
    )

    name = models.CharField(_('name'), max_length=255)
    code = models.CharField(_('code'), max_length=100)
    description = models.TextField(_('description'), blank=True)

    # Display
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    color = models.CharField(_('color'), max_length=7, blank=True)
    icon = models.CharField(_('icon'), max_length=50, blank=True)

    is_active = models.BooleanField(_('is active'), default=True)

    # Metadata for external integrations
    external_id = models.CharField(_('external ID'), max_length=255, blank=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)

    class Meta:
        verbose_name = _('label value')
        verbose_name_plural = _('label values')
        ordering = ['label_definition', 'display_order', 'name']
        unique_together = [['label_definition', 'code']]
        indexes = [
            models.Index(fields=['label_definition', 'is_active']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    @property
    def full_path(self):
        """Get full hierarchical path."""
        path = [self.name]
        current = self.parent
        while current:
            path.insert(0, current.name)
            current = current.parent
        return ' > '.join(path)

    @property
    def depth(self):
        """Calculate depth in hierarchy."""
        depth = 0
        current = self.parent
        while current:
            depth += 1
            current = current.parent
        return depth


# =============================================================================
# LABEL ASSIGNMENTS - Linking labels to entities
# =============================================================================

class CampaignLabel(BaseModel):
    """
    Campaign Label Assignment - Links labels to campaigns.
    """
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.CASCADE,
        related_name='labels',
        verbose_name=_('campaign')
    )
    label_value = models.ForeignKey(
        LabelValue,
        on_delete=models.CASCADE,
        related_name='campaign_assignments',
        verbose_name=_('label value')
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_campaign_labels',
        verbose_name=_('assigned by'),
        null=True
    )

    class Meta:
        verbose_name = _('campaign label')
        verbose_name_plural = _('campaign labels')
        unique_together = [['campaign', 'label_value']]

    def __str__(self):
        return f"{self.campaign.name} - {self.label_value.name}"


class MediaPlanLabel(BaseModel):
    """
    Media Plan Label Assignment - Links labels to media plans.
    """
    media_plan = models.ForeignKey(
        'campaigns.MediaPlan',
        on_delete=models.CASCADE,
        related_name='labels',
        verbose_name=_('media plan')
    )
    label_value = models.ForeignKey(
        LabelValue,
        on_delete=models.CASCADE,
        related_name='media_plan_assignments',
        verbose_name=_('label value')
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_media_plan_labels',
        verbose_name=_('assigned by'),
        null=True
    )

    class Meta:
        verbose_name = _('media plan label')
        verbose_name_plural = _('media plan labels')
        unique_together = [['media_plan', 'label_value']]

    def __str__(self):
        return f"{self.media_plan.name} - {self.label_value.name}"


class SubcampaignLabel(BaseModel):
    """
    Subcampaign Label Assignment - Links labels to subcampaigns.
    """
    subcampaign = models.ForeignKey(
        'campaigns.Subcampaign',
        on_delete=models.CASCADE,
        related_name='labels',
        verbose_name=_('subcampaign')
    )
    label_value = models.ForeignKey(
        LabelValue,
        on_delete=models.CASCADE,
        related_name='subcampaign_assignments',
        verbose_name=_('label value')
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_subcampaign_labels',
        verbose_name=_('assigned by'),
        null=True
    )

    class Meta:
        verbose_name = _('subcampaign label')
        verbose_name_plural = _('subcampaign labels')
        unique_together = [['subcampaign', 'label_value']]

    def __str__(self):
        return f"{self.subcampaign.name} - {self.label_value.name}"


class ProjectLabel(BaseModel):
    """
    Project Label Assignment - Links labels to projects.
    """
    project = models.ForeignKey(
        'campaigns.Project',
        on_delete=models.CASCADE,
        related_name='labels',
        verbose_name=_('project')
    )
    label_value = models.ForeignKey(
        LabelValue,
        on_delete=models.CASCADE,
        related_name='project_assignments',
        verbose_name=_('label value')
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_project_labels',
        verbose_name=_('assigned by'),
        null=True
    )

    class Meta:
        verbose_name = _('project label')
        verbose_name_plural = _('project labels')
        unique_together = [['project', 'label_value']]

    def __str__(self):
        return f"{self.project.name} - {self.label_value.name}"
