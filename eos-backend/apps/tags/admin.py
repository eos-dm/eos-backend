from django.contrib import admin
from .models import EosTag, EosTaggedItem


@admin.register(EosTag)
class EosTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'scope_level', 'is_active', 'created_at']
    list_filter = ['scope_level', 'is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(EosTaggedItem)
class EosTaggedItemAdmin(admin.ModelAdmin):
    list_display = ['tag', 'entity_type', 'entity_id', 'created_at']
    list_filter = ['entity_type', 'tag']
    search_fields = ['entity_type']
