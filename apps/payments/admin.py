from django.contrib import admin
from .models import (
    PaymentMethod, SubcampaignPaymentType, PricingAdjustmentRule
)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['id', 'cost_center', 'advertiser', 'payment_type', 'media_unit_type', 'fee_type', 'is_active']
    list_filter = ['payment_type', 'fee_type', 'is_active', 'cost_center']
    search_fields = ['cost_center__name', 'advertiser__name']


@admin.register(SubcampaignPaymentType)
class SubcampaignPaymentTypeAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'subcampaign', 'start_date', 'end_date',
        'fee_type', 'fee_value', 'is_fee_value_overwritten'
    ]
    list_filter = ['fee_type', 'is_fee_value_overwritten']
    search_fields = ['subcampaign__name', 'subcampaign__subcampaign_code']
    date_hierarchy = 'start_date'


@admin.register(PricingAdjustmentRule)
class PricingAdjustmentRuleAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'target_kind', 'cost_center', 'client', 'advertiser',
        'payment_method', 'start_date', 'end_date',
        'adjustment_kind', 'adjustment_value_micros',
        'is_adjustment_value_micros_overwritten', 'is_active'
    ]
    list_filter = ['target_kind', 'adjustment_kind', 'is_active', 'is_adjustment_value_micros_overwritten']
    search_fields = ['cost_center__name', 'client__name', 'advertiser__name']
    date_hierarchy = 'start_date'
