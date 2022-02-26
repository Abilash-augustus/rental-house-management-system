from django.contrib import admin

from utilities_and_rent.models import (PaymentMethods, RentPayment,
                                     UnitRentDetails)


@admin.register(UnitRentDetails)
class UnitRentDetailsAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'unit', 'rent_amount', 'pay_for_month', 'cleared', 'due_date']
    list_editable = ['rent_amount',]
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):
    pass

@admin.register(PaymentMethods)
class PaymentMethodsAdmin(admin.ModelAdmin):
    pass