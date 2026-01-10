"""
Geographic Models - GeoNames-based location data
Based on EOS Schema V66
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class GeoCountry(models.Model):
    """
    Geographic Country - ISO 3166-1 alpha-2 country codes.
    V66: iso_code char(2) [pk]
    """
    iso_code = models.CharField(_('ISO code'), max_length=2, primary_key=True)
    geoname_id = models.IntegerField(_('GeoName ID'), unique=True, null=True, blank=True)
    name = models.CharField(_('name'), max_length=100)
    phone_prefix = models.CharField(_('phone prefix'), max_length=10, blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        ordering = ['name']
        db_table = 'geo_country'

    def __str__(self):
        return f"{self.name} ({self.iso_code})"


class GeoState(models.Model):
    """
    Geographic State/Province/Region.
    V66: geoname_id int [pk]
    """
    geoname_id = models.IntegerField(_('GeoName ID'), primary_key=True)
    country = models.ForeignKey(
        GeoCountry,
        on_delete=models.CASCADE,
        related_name='states',
        verbose_name=_('country'),
        db_column='country_iso_code'
    )
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=10, blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('state')
        verbose_name_plural = _('states')
        ordering = ['name']
        db_table = 'geo_state'

    def __str__(self):
        return f"{self.name}, {self.country.iso_code}"


class GeoCity(models.Model):
    """
    Geographic City.
    V66: geoname_id int [pk]
    """
    geoname_id = models.IntegerField(_('GeoName ID'), primary_key=True)
    state = models.ForeignKey(
        GeoState,
        on_delete=models.CASCADE,
        related_name='cities',
        verbose_name=_('state'),
        null=True,
        blank=True,
        db_column='state_geoname_id'
    )
    name = models.CharField(_('name'), max_length=100)
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(_('longitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    timezone_code = models.CharField(_('timezone code'), max_length=100, blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        ordering = ['name']
        db_table = 'geo_city'

    def __str__(self):
        return self.name


class GeoCityCountry(models.Model):
    """
    City-Country mapping (for cities that span multiple countries).
    V66: city_geoname_id int [pk], country_iso_code char(2) [pk]
    """
    city = models.ForeignKey(
        GeoCity,
        on_delete=models.CASCADE,
        related_name='countries',
        verbose_name=_('city'),
        db_column='city_geoname_id'
    )
    country = models.ForeignKey(
        GeoCountry,
        on_delete=models.CASCADE,
        related_name='cities',
        verbose_name=_('country'),
        db_column='country_iso_code'
    )
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('city-country mapping')
        verbose_name_plural = _('city-country mappings')
        db_table = 'geo_city_country'
        constraints = [
            models.UniqueConstraint(
                fields=['city', 'country'],
                name='ux_geo_city_country'
            )
        ]

    def __str__(self):
        return f"{self.city.name} - {self.country.iso_code}"


class GeoPostalCode(models.Model):
    """
    Geographic Postal Code.
    V66: id int [pk, increment]
    """
    postal_code = models.CharField(_('postal code'), max_length=20)
    city = models.ForeignKey(
        GeoCity,
        on_delete=models.CASCADE,
        related_name='postal_codes',
        verbose_name=_('city'),
        db_column='city_geoname_id'
    )
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(_('longitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('postal code')
        verbose_name_plural = _('postal codes')
        db_table = 'geo_postal_code'
        constraints = [
            models.UniqueConstraint(
                fields=['postal_code', 'city'],
                name='ux_geo_postal_code_postal_city'
            )
        ]

    def __str__(self):
        return f"{self.postal_code} - {self.city.name}"
