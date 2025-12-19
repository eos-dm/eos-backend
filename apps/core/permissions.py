"""
Core Permissions - Multi-tenant access control
"""
from rest_framework import permissions


class IsTenantAdmin(permissions.BasePermission):
    """
    Permission to check if user is admin of the tenant.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        # Get tenant from object
        tenant = getattr(obj, 'tenant', None)
        if not tenant:
            # Try to get tenant from related object
            if hasattr(obj, 'agency'):
                tenant = obj.agency.tenant
            elif hasattr(obj, 'client'):
                tenant = obj.client.agency.tenant

        if tenant:
            return request.user.is_tenant_admin(tenant)
        return False


class CanAccessAgency(permissions.BasePermission):
    """
    Permission to check if user can access the agency.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        # Get agency from object
        agency = obj if hasattr(obj, 'clients') else getattr(obj, 'agency', None)
        if not agency:
            if hasattr(obj, 'client'):
                agency = obj.client.agency

        if agency:
            return request.user.can_access_agency(agency)
        return False


class CanAccessClient(permissions.BasePermission):
    """
    Permission to check if user can access the client.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        # Get client from object
        client = obj if hasattr(obj, 'advertisers') else getattr(obj, 'client', None)

        if client:
            return request.user.can_access_client(client)
        return False


class IsFinanceUser(permissions.BasePermission):
    """
    Permission for finance-specific operations.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__icontains='finance').exists()


class IsPlannerUser(permissions.BasePermission):
    """
    Permission for planner-specific operations.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__icontains='planner').exists()


class IsOperationsUser(permissions.BasePermission):
    """
    Permission for operations-specific operations.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__icontains='operations').exists()


class IsClientPortalUser(permissions.BasePermission):
    """
    Permission for client portal users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_client_portal_user


class CanApprove(permissions.BasePermission):
    """
    Permission to approve workflows.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.has_perm('workflows.can_approve')

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        # Check if user can approve this specific object
        return request.user.can_approve_object(obj)


class ReadOnly(permissions.BasePermission):
    """
    Read-only permission for safe methods.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
