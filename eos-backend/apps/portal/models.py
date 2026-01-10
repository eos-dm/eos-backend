"""
Portal Models - Client Portal specific models
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel


class ClientPortalSettings(BaseModel):
    """
    Client Portal Settings - Configuration for client portal access.
    """
    client = models.OneToOneField(
        'core.Client',
        on_delete=models.CASCADE,
        related_name='portal_settings',
        verbose_name=_('client')
    )

    # Features
    can_view_campaigns = models.BooleanField(_('can view campaigns'), default=True)
    can_view_media_plans = models.BooleanField(_('can view media plans'), default=True)
    can_view_budgets = models.BooleanField(_('can view budgets'), default=False)
    can_view_reports = models.BooleanField(_('can view reports'), default=True)
    can_download_reports = models.BooleanField(_('can download reports'), default=True)
    can_approve = models.BooleanField(_('can approve'), default=True)
    can_comment = models.BooleanField(_('can comment'), default=True)

    # Customization
    welcome_message = models.TextField(_('welcome message'), blank=True)
    custom_logo = models.ImageField(
        _('custom logo'),
        upload_to='portal/logos/',
        blank=True,
        null=True
    )
    primary_color = models.CharField(_('primary color'), max_length=7, default='#3B82F6')

    # Notifications
    email_on_new_campaign = models.BooleanField(_('email on new campaign'), default=True)
    email_on_approval_request = models.BooleanField(_('email on approval request'), default=True)
    email_on_status_change = models.BooleanField(_('email on status change'), default=True)

    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('client portal settings')
        verbose_name_plural = _('client portal settings')

    def __str__(self):
        return f"Portal settings for {self.client.name}"


class PortalMessage(BaseModel):
    """
    Portal Message - Messages/communications in client portal.
    """
    client = models.ForeignKey(
        'core.Client',
        on_delete=models.CASCADE,
        related_name='portal_messages',
        verbose_name=_('client')
    )
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.CASCADE,
        related_name='portal_messages',
        verbose_name=_('campaign'),
        null=True,
        blank=True
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='sent_portal_messages',
        verbose_name=_('sender'),
        null=True
    )
    subject = models.CharField(_('subject'), max_length=255)
    content = models.TextField(_('content'))

    # Read tracking
    is_read = models.BooleanField(_('is read'), default=False)
    read_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='read_portal_messages',
        verbose_name=_('read by'),
        null=True,
        blank=True
    )
    read_at = models.DateTimeField(_('read at'), null=True, blank=True)

    # Attachments handled separately
    has_attachments = models.BooleanField(_('has attachments'), default=False)

    class Meta:
        verbose_name = _('portal message')
        verbose_name_plural = _('portal messages')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.client.name}"


class PortalMessageAttachment(BaseModel):
    """
    Portal Message Attachment - Files attached to portal messages.
    """
    message = models.ForeignKey(
        PortalMessage,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('message')
    )
    name = models.CharField(_('name'), max_length=255)
    file = models.FileField(_('file'), upload_to='portal/attachments/')
    file_size = models.PositiveIntegerField(_('file size'), default=0)
    mime_type = models.CharField(_('MIME type'), max_length=100, blank=True)

    class Meta:
        verbose_name = _('portal message attachment')
        verbose_name_plural = _('portal message attachments')

    def __str__(self):
        return self.name


class PortalActivityLog(BaseModel):
    """
    Portal Activity Log - Track client portal user activity.
    """
    ACTION_CHOICES = [
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('view_campaign', _('View Campaign')),
        ('view_media_plan', _('View Media Plan')),
        ('view_report', _('View Report')),
        ('download_report', _('Download Report')),
        ('approve', _('Approve')),
        ('reject', _('Reject')),
        ('comment', _('Comment')),
        ('message', _('Message')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portal_activities',
        verbose_name=_('user')
    )
    client = models.ForeignKey(
        'core.Client',
        on_delete=models.CASCADE,
        related_name='portal_activities',
        verbose_name=_('client')
    )

    action = models.CharField(_('action'), max_length=30, choices=ACTION_CHOICES)
    entity_type = models.CharField(_('entity type'), max_length=50, blank=True)
    entity_id = models.UUIDField(_('entity ID'), null=True, blank=True)
    entity_name = models.CharField(_('entity name'), max_length=255, blank=True)

    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)

    class Meta:
        verbose_name = _('portal activity log')
        verbose_name_plural = _('portal activity logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['client', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.created_at}"
