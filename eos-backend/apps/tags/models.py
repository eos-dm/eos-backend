"""
Tags Models - EOS Tagging System
Based on EOS Schema V66

Tags can be scoped at various hierarchy levels:
tenant, agency, cost_center, client, advertiser, project, media_plan
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel


class ScopeLevel(models.TextChoices):
    TENANT = 'tenant', _('Tenant')
    AGENCY = 'agency', _('Agency')
    COST_CENTER = 'cost_center', _('Cost Center')
    CLIENT = 'client', _('Client')
    ADVERTISER = 'advertiser', _('Advertiser')
    PROJECT = 'project', _('Project')
    MEDIA_PLAN = 'media_plan', _('Media Plan')


class EosTag(BaseModel):
    """
    EOS Tag - Tags for categorizing entities.
    V66: id uuid [pk], scope_level varchar(30) [not null]
    """
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255)

    scope_level = models.CharField(
        _('scope level'),
        max_length=30,
        choices=ScopeLevel.choices
    )

    # Scope references (based on scope_level)
    tenant = models.ForeignKey(
        'core.Tenant',
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name=_('tenant'),
        null=True,
        blank=True
    )
    agency = models.ForeignKey(
        'core.Agency',
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name=_('agency'),
        null=True,
        blank=True
    )
    cost_center = models.ForeignKey(
        'core.CostCenter',
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name=_('cost center'),
        null=True,
        blank=True
    )
    client = models.ForeignKey(
        'core.Client',
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name=_('client'),
        null=True,
        blank=True
    )
    advertiser = models.ForeignKey(
        'core.Advertiser',
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name=_('advertiser'),
        null=True,
        blank=True
    )
    project = models.ForeignKey(
        'campaigns.Project',
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name=_('project'),
        null=True,
        blank=True
    )
    media_plan = models.ForeignKey(
        'campaigns.MediaPlan',
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name=_('media plan'),
        null=True,
        blank=True
    )

    is_active = models.BooleanField(_('is active'), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_tags',
        verbose_name=_('created by'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['scope_level', 'tenant', 'slug'],
                name='ux_eos_tag_scope_tenant_slug'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.scope_level})"


class EosTaggedItem(BaseModel):
    """
    EOS Tagged Item - Associates tags with entities.
    V66: id uuid [pk], entity_type varchar(50) [not null], entity_id uuid [not null]
    """
    tag = models.ForeignKey(
        EosTag,
        on_delete=models.CASCADE,
        related_name='tagged_items',
        verbose_name=_('tag')
    )

    entity_type = models.CharField(_('entity type'), max_length=50)
    entity_id = models.UUIDField(_('entity ID'))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='tagged_items',
        verbose_name=_('created by'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('tagged item')
        verbose_name_plural = _('tagged items')
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'entity_type', 'entity_id'],
                name='ux_eos_tagged_item_tag_entity'
            )
        ]
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
        ]

    def __str__(self):
        return f"{self.tag.name} → {self.entity_type}:{self.entity_id}"
