"""
Accounts Admin - User Management Administration
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, TenantMembership, AgencyMembership, ClientMembership,
    UserNotificationPreference, UserSession
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'role', 'is_active', 'is_staff', 'last_login']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'role', 'is_client_portal_user']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        (_('Role & Permissions'), {
            'fields': ('role', 'is_client_portal_user', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Preferences'), {'fields': ('language', 'timezone')}),
        (_('Security'), {'fields': ('two_factor_enabled', 'last_login_ip')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )

    readonly_fields = ['last_login', 'date_joined', 'created_at', 'updated_at', 'last_login_ip']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )


class TenantMembershipInline(admin.TabularInline):
    model = TenantMembership
    extra = 1


class AgencyMembershipInline(admin.TabularInline):
    model = AgencyMembership
    extra = 1


class ClientMembershipInline(admin.TabularInline):
    model = ClientMembership
    extra = 1


@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'role', 'is_default', 'created_at']
    list_filter = ['role', 'is_default', 'tenant']
    search_fields = ['user__email', 'tenant__name']


@admin.register(AgencyMembership)
class AgencyMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'agency', 'role', 'created_at']
    list_filter = ['role', 'agency']
    search_fields = ['user__email', 'agency__name']


@admin.register(ClientMembership)
class ClientMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'client', 'role', 'can_approve', 'can_view_financials', 'created_at']
    list_filter = ['role', 'can_approve', 'can_view_financials']
    search_fields = ['user__email', 'client__name']


@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_campaign_status', 'email_approval_required', 'email_weekly_summary']
    search_fields = ['user__email']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'is_active', 'created_at', 'last_activity']
    list_filter = ['is_active']
    search_fields = ['user__email', 'ip_address']
    readonly_fields = ['id', 'session_key', 'user_agent', 'created_at', 'last_activity']
