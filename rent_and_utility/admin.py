from django.contrib import admin
from rent_and_utility.models import UnitRentDetails, RentPayment






@admin.register(UnitRentDetails)
class UnitRentDetailsAdmin(admin.ModelAdmin):
    pass

@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):
    pass