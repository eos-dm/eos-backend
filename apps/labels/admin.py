"""
Labels Admin - Taxonomy Administration
"""
from django.contrib import admin
from django.conf import settings
from .models import (
    LabelDefinition, LabelLevel, LabelValue,
    CampaignLabel, MediaPlanLabel, SubcampaignLabel, ProjectLabel
)


class LabelLevelInline(admin.TabularInline):
    model = LabelLevel
    extra = 1
    ordering = ['level_number']


class LabelValueInline(admin.TabularInline):
    model = LabelValue
    extra = 1
    fields = ['name', 'code', 'parent', 'label_level', 'display_order', 'is_active']
    ordering = ['display_order', 'name']


@admin.register(LabelDefinition)
class LabelDefinitionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'code', 'tenant', 'data_type', 'applies_to',
        'is_required', 'is_active', 'display_order', 'values_count'
    ]
    list_filter = ['tenant', 'data_type', 'applies_to', 'is_required', 'is_active']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [LabelLevelInline, LabelValueInline]

    fieldsets = (
        (None, {
            'fields': ('tenant', 'name', 'code', 'description')
        }),
        ('Configuration', {
            'fields': ('data_type', 'applies_to', 'display_order')
        }),
        ('Constraints', {
            'fields': ('is_required', 'is_active')
        }),
        ('Display', {
            'fields': ('color', 'icon')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def values_count(self, obj):
        return obj.values.count()
    values_count.short_description = 'Values'

    def get_readonly_fields(self, request, obj=None):
        """Make tenant read-only after creation."""
        if obj:
            return self.readonly_fields + ['tenant']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        """Validate max labels before saving."""
        if not change:  # Only on creation
            max_labels = getattr(settings, 'MAX_LABEL_DEFINITIONS', 20)
            current_count = LabelDefinition.objects.filter(tenant=obj.tenant).count()
            if current_count >= max_labels:
                from django.contrib import messages
                messages.error(
                    request,
                    f'Cannot create label definition. Maximum of {max_labels} allowed per tenant.'
                )
                return
        super().save_model(request, obj, form, change)


@admin.register(LabelLevel)
class LabelLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'label_definition', 'level_number', 'is_active']
    list_filter = ['label_definition__tenant', 'is_active']
    search_fields = ['name', 'label_definition__name']
    ordering = ['label_definition', 'level_number']


@admin.register(LabelValue)
class LabelValueAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'code', 'label_definition', 'label_level',
        'parent', 'display_order', 'is_active'
    ]
    list_filter = [
        'label_definition__tenant', 'label_definition',
        'label_level', 'is_active'
    ]
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'full_path', 'depth']
    ordering = ['label_definition', 'display_order', 'name']

    fieldsets = (
        (None, {
            'fields': ('label_definition', 'label_level', 'parent')
        }),
        ('Value', {
            'fields': ('name', 'code', 'description')
        }),
        ('Display', {
            'fields': ('display_order', 'color', 'icon')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('External', {
            'fields': ('external_id', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Hierarchy Info', {
            'fields': ('full_path', 'depth'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CampaignLabel)
class CampaignLabelAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'label_value', 'assigned_by', 'created_at']
    list_filter = ['label_value__label_definition']
    search_fields = ['campaign__name', 'label_value__name']
    raw_id_fields = ['campaign', 'label_value', 'assigned_by']


@admin.register(MediaPlanLabel)
class MediaPlanLabelAdmin(admin.ModelAdmin):
    list_display = ['media_plan', 'label_value', 'assigned_by', 'created_at']
    list_filter = ['label_value__label_definition']
    search_fields = ['media_plan__name', 'label_value__name']
    raw_id_fields = ['media_plan', 'label_value', 'assigned_by']


@admin.register(SubcampaignLabel)
class SubcampaignLabelAdmin(admin.ModelAdmin):
    list_display = ['subcampaign', 'label_value', 'assigned_by', 'created_at']
    list_filter = ['label_value__label_definition']
    search_fields = ['subcampaign__name', 'label_value__name']
    raw_id_fields = ['subcampaign', 'label_value', 'assigned_by']


@admin.register(ProjectLabel)
class ProjectLabelAdmin(admin.ModelAdmin):
    list_display = ['project', 'label_value', 'assigned_by', 'created_at']
    list_filter = ['label_value__label_definition']
    search_fields = ['project__name', 'label_value__name']
    raw_id_fields = ['project', 'label_value', 'assigned_by']
