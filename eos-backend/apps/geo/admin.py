from django.contrib import admin
from .models import GeoCountry, GeoState, GeoCity, GeoCityCountry, GeoPostalCode


@admin.register(GeoCountry)
class GeoCountryAdmin(admin.ModelAdmin):
    list_display = ['iso_code', 'name', 'phone_prefix', 'is_active']
    list_filter = ['is_active']
    search_fields = ['iso_code', 'name']
    ordering = ['name']


@admin.register(GeoState)
class GeoStateAdmin(admin.ModelAdmin):
    list_display = ['geoname_id', 'name', 'code', 'country', 'is_active']
    list_filter = ['country', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(GeoCity)
class GeoCityAdmin(admin.ModelAdmin):
    list_display = ['geoname_id', 'name', 'state', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']


@admin.register(GeoCityCountry)
class GeoCityCountryAdmin(admin.ModelAdmin):
    list_display = ['city', 'country', 'is_active']
    list_filter = ['country', 'is_active']


@admin.register(GeoPostalCode)
class GeoPostalCodeAdmin(admin.ModelAdmin):
    list_display = ['postal_code', 'city', 'is_active']
    list_filter = ['is_active']
    search_fields = ['postal_code']
