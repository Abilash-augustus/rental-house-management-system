from django.contrib import admin

from utilities_and_rent.models import (ElectricityBilling, ElectricityPayments,
                                       ElectricityReadings, PaymentMethods,
                                       RentPayment, UnitRentDetails,
                                       WaterBilling, WaterPayments, WaterConsumption)


@admin.register(UnitRentDetails)
class UnitRentDetailsAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'unit', 'rent_amount', 'pay_for_month', 'cleared', 'due_date']
    list_editable = ['rent_amount',]
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):
    list_display = ['rent_details','manager','payment_code','amount','paid_for_month','paid_on','payment_method', 'status','payment_method']
    list_filter = ('status','added_on')
    search_fields = ('payment_code',)

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
    list_display = ['tenant','bill_code','quantity','measuring_unit','total','total','cleared','added']
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
    
