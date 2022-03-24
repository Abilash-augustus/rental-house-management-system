from django.contrib import admin

from utilities.models import (ElectricityBilling, ElectricityMeter,
                                       ElectricityPayments,
                                       ElectricityReadings, PayOnlineMpesa,
                                       PaymentMethods, RentPayment,
                                       UnitRentDetails, WaterBilling,
                                       WaterConsumption, WaterMeter,
                                       WaterPayments,RentIncrementNotice)


@admin.register(UnitRentDetails)
class UnitRentDetailsAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'unit', 'rent_amount', 'pay_for_month', 'cleared', 'due_date']
    """
    def has_change_permission(self, request, obj=None):
        return False
"""
@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):
    list_display = ['rent_details','manager','payment_code','amount','paid_for_month','paid_on','payment_method','paid_with_stripe', 'status','added_on']
    list_filter = ('status','paid_with_stripe','added_on')
    search_fields = ('payment_code',)
    
@admin.register(RentIncrementNotice)
class RentIncrementNoticeAdmin(admin.ModelAdmin):
    list_display = ['ref_code','re','takes_effect_on','notify_all','created']
    list_filter = ['created','notify_all','building']
    search_fields = ['ref_code','re','takes_effect_on']

@admin.register(PaymentMethods)
class PaymentMethodsAdmin(admin.ModelAdmin):
    list_display = ['name','account_name','paybill_number','account_number','added']

class WaterConsumptionAdmin(admin.StackedInline):
    model = WaterConsumption

@admin.register(WaterPayments)
class WaterPaymentsAdmin(admin.ModelAdmin):
    pass
    
@admin.register(WaterBilling)
class WaterBillingAdmin(admin.ModelAdmin):
    list_display = ['tenant','bill_code','units','total','total','cleared','added']
    search_fields = ['bill_code','tenant']
    inlines = [WaterConsumptionAdmin]
    
class ElectricityReadingsAdmin(admin.StackedInline):
    model = ElectricityReadings

@admin.register(ElectricityBilling)
class ElectricityBillingAdmin(admin.ModelAdmin):
    list_display = ['tenant','bill_code','rental_unit','measuring_unit','total','month','due_date','cleared','added']
    inlines = [ElectricityReadingsAdmin]
    
@admin.register(ElectricityPayments)
class ElectricityPaymentsAdmin(admin.ModelAdmin):
    list_display = ['parent','tracking_code','payment_code','amount','payment_method','status','created']
    

@admin.register(WaterMeter)
class WaterMeterAdmin(admin.ModelAdmin):
    pass

@admin.register(ElectricityMeter)
class ElectricityMeterAdmin(admin.ModelAdmin):
    pass

@admin.register(PayOnlineMpesa)
class PayOnlineMpesaAdmin(admin.ModelAdmin):
    list_display = ['first_name','middle_name','last_name','amount','paid_for',]