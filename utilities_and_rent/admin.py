from django.contrib import admin

from utilities_and_rent.models import (PaymentMethods, RentPayment,
                                     UnitRentDetails, WaterBilling, WaterConsumption)


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
    pass

class WaterConsumptionAdmin(admin.StackedInline):
    model = WaterConsumption
    
@admin.register(WaterBilling)
class WaterAdmin(admin.ModelAdmin):
    inlines = [WaterConsumptionAdmin]
    """def get_inline_instances(self,request,obj=None):
        if not obj:
            return list()
        return super(WaterAdmin,self).get_inline_instances(request,obj)"""