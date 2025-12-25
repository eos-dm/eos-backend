from django.contrib import admin
from .models import AuditLog, BudgetChangeLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'entity_type', 'entity_id', 'action',
        'old_state', 'new_state', 'created_by', 'created_at'
    ]
    list_filter = ['entity_type', 'action', 'created_at']
    search_fields = ['entity_id', 'description', 'created_by__email']
    date_hierarchy = 'created_at'
    readonly_fields = [
        'id', 'entity_type', 'entity_id', 'action', 'description',
        'old_state', 'new_state', 'extra_data', 'created_by',
        'created_at', 'ip_address', 'user_agent'
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BudgetChangeLog)
class BudgetChangeLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'entity_type', 'entity_id', 'field_name',
        'old_value_micros', 'new_value_micros', 'is_manual_override',
        'changed_by', 'changed_at'
    ]
    list_filter = ['entity_type', 'field_name', 'is_manual_override', 'changed_at']
    search_fields = ['entity_id', 'reason', 'changed_by__email']
    date_hierarchy = 'changed_at'
    readonly_fields = [
        'id', 'entity_type', 'entity_id', 'field_name',
        'old_value_micros', 'new_value_micros', 'reason',
        'is_manual_override', 'changed_by', 'changed_at',
        'entity_state', 'pricing_model_id'
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
