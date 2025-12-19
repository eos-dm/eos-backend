"""
Accounts Models - Custom User Model and Role Management
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.utils.translation import gettext_lazy as _
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User Model - Email-based authentication with role support.
    """
    ROLE_CHOICES = [
        ('superadmin', _('Super Admin')),
        ('tenant_admin', _('Tenant Admin')),
        ('planner', _('Planner')),
        ('operations', _('Operations')),
        ('finance', _('Finance')),
        ('accounts', _('Accounts')),
        ('client', _('Client')),
        ('viewer', _('Viewer')),
    ]

    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('es', _('Spanish')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)

    # Profile
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    phone = models.CharField(_('phone'), max_length=50, blank=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True, null=True)

    # Role and permissions
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer'
    )
    is_client_portal_user = models.BooleanField(
        _('is client portal user'),
        default=False,
        help_text=_('Designates whether this user accesses the client portal.')
    )

    # Preferences
    language = models.CharField(
        _('language'),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='en'
    )
    timezone = models.CharField(_('timezone'), max_length=50, default='Europe/Madrid')

    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    last_login_ip = models.GenericIPAddressField(_('last login IP'), null=True, blank=True)

    # 2FA (for future implementation)
    two_factor_enabled = models.BooleanField(_('2FA enabled'), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['email']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_accessible_tenant_ids(self):
        """Get list of tenant IDs this user can access."""
        if self.is_superuser:
            from apps.core.models import Tenant
            return list(Tenant.objects.values_list('id', flat=True))
        return list(self.tenant_memberships.values_list('tenant_id', flat=True))

    def is_tenant_admin(self, tenant):
        """Check if user is admin of the given tenant."""
        if self.is_superuser:
            return True
        return self.tenant_memberships.filter(
            tenant=tenant,
            role__in=['tenant_admin', 'admin']
        ).exists()

    def can_access_agency(self, agency):
        """Check if user can access the given agency."""
        if self.is_superuser:
            return True
        return self.agency_memberships.filter(agency=agency).exists()

    def can_access_client(self, client):
        """Check if user can access the given client."""
        if self.is_superuser:
            return True
        # Check direct client membership
        if self.client_memberships.filter(client=client).exists():
            return True
        # Check agency membership
        return self.can_access_agency(client.agency)

    def can_approve_object(self, obj):
        """Check if user can approve the given object."""
        if self.is_superuser:
            return True
        # Check if user has approval permission for this object
        return self.role in ['tenant_admin', 'planner', 'operations']


class TenantMembership(models.Model):
    """
    Tenant Membership - Links users to tenants with roles.
    """
    ROLE_CHOICES = [
        ('admin', _('Admin')),
        ('member', _('Member')),
        ('viewer', _('Viewer')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tenant_memberships',
        verbose_name=_('user')
    )
    tenant = models.ForeignKey(
        'core.Tenant',
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('tenant')
    )
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default='member')
    is_default = models.BooleanField(_('is default'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('tenant membership')
        verbose_name_plural = _('tenant memberships')
        unique_together = [['user', 'tenant']]

    def __str__(self):
        return f"{self.user.email} - {self.tenant.name} ({self.role})"


class AgencyMembership(models.Model):
    """
    Agency Membership - Links users to agencies with roles.
    """
    ROLE_CHOICES = [
        ('admin', _('Admin')),
        ('planner', _('Planner')),
        ('operations', _('Operations')),
        ('finance', _('Finance')),
        ('accounts', _('Accounts')),
        ('viewer', _('Viewer')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='agency_memberships',
        verbose_name=_('user')
    )
    agency = models.ForeignKey(
        'core.Agency',
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('agency')
    )
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default='viewer')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('agency membership')
        verbose_name_plural = _('agency memberships')
        unique_together = [['user', 'agency']]

    def __str__(self):
        return f"{self.user.email} - {self.agency.name} ({self.role})"


class ClientMembership(models.Model):
    """
    Client Membership - Links users (client contacts) to clients.
    For client portal access.
    """
    ROLE_CHOICES = [
        ('admin', _('Admin')),
        ('approver', _('Approver')),
        ('viewer', _('Viewer')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='client_memberships',
        verbose_name=_('user')
    )
    client = models.ForeignKey(
        'core.Client',
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('client')
    )
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default='viewer')
    can_approve = models.BooleanField(_('can approve'), default=False)
    can_view_financials = models.BooleanField(_('can view financials'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('client membership')
        verbose_name_plural = _('client memberships')
        unique_together = [['user', 'client']]

    def __str__(self):
        return f"{self.user.email} - {self.client.name} ({self.role})"


class UserNotificationPreference(models.Model):
    """
    User Notification Preferences - Control which notifications users receive.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name=_('user')
    )

    # Email notifications
    email_campaign_status = models.BooleanField(_('email on campaign status change'), default=True)
    email_approval_required = models.BooleanField(_('email on approval required'), default=True)
    email_approval_completed = models.BooleanField(_('email on approval completed'), default=True)
    email_budget_alerts = models.BooleanField(_('email on budget alerts'), default=True)
    email_weekly_summary = models.BooleanField(_('weekly summary email'), default=True)

    # In-app notifications
    inapp_campaign_status = models.BooleanField(_('in-app on campaign status change'), default=True)
    inapp_approval_required = models.BooleanField(_('in-app on approval required'), default=True)
    inapp_comments = models.BooleanField(_('in-app on comments'), default=True)

    class Meta:
        verbose_name = _('notification preference')
        verbose_name_plural = _('notification preferences')

    def __str__(self):
        return f"Preferences for {self.user.email}"


class UserSession(models.Model):
    """
    User Session - Track active sessions for security.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name=_('user')
    )
    session_key = models.CharField(_('session key'), max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(_('IP address'))
    user_agent = models.TextField(_('user agent'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    last_activity = models.DateTimeField(_('last activity'), auto_now=True)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('user session')
        verbose_name_plural = _('user sessions')
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"
