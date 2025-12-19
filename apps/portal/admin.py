"""
Portal Admin - Client Portal Administration
"""
from django.contrib import admin
from .models import (
    ClientPortalSettings, PortalMessage, PortalMessageAttachment, PortalActivityLog
)


@admin.register(ClientPortalSettings)
class ClientPortalSettingsAdmin(admin.ModelAdmin):
    list_display = ['client', 'is_active', 'can_approve', 'can_comment']
    list_filter = ['is_active', 'can_approve', 'can_view_budgets']
    search_fields = ['client__name']


class PortalMessageAttachmentInline(admin.TabularInline):
    model = PortalMessageAttachment
    extra = 0


@admin.register(PortalMessage)
class PortalMessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'client', 'sender', 'is_read', 'created_at']
    list_filter = ['is_read', 'client']
    search_fields = ['subject', 'content', 'sender__email']
    inlines = [PortalMessageAttachmentInline]


@admin.register(PortalActivityLog)
class PortalActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'client', 'action', 'entity_type', 'created_at']
    list_filter = ['action', 'client', 'created_at']
    search_fields = ['user__email', 'entity_name']
    readonly_fields = ['created_at']
