from django import forms
from rental_property.models import RentalUnit

from utilities_and_rent.models import (ElectricityBilling, ElectricityMeter, ElectricityPayments,
                                       ElectricityReadings, RentPayment,
                                       UnitRentDetails, WaterBilling,
                                       WaterConsumption, WaterMeter, WaterPayments)


class DateInput(forms.DateInput):
    input_type = 'date'
    
class AddRentDetailsForm(forms.ModelForm):
    class Meta:
        model = UnitRentDetails
        fields = ['rent_amount','currency','amount_paid','pay_for_month','start_date',
                  'end_date','due_date','notify_tenant']
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
            'due_date': DateInput(),
        }

class SubmitPaymentsForm(forms.ModelForm):
    class Meta:
        model = RentPayment
        fields = ['payment_code', 'amount', 'payment_method', 'paid_on']   
        widgets = {
            'paid_on': DateInput(),
        } 
        
class UpdateRentDetails(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateRentDetails, self).__init__(*args, **kwargs)
        self.fields['currency'].disabled = True
        self.fields['added'].disabled = True
        self.fields['amount_paid'].disabled = True
    class Meta:
        model = UnitRentDetails
        fields = ['currency','rent_amount','amount_paid','pay_for_month',
                  'cleared','start_date','rent_type','end_date','added','due_date','status','notify_tenant']
        widgets = {
            'due_date': DateInput(),
        }
        
class PaymentUpdateForm(forms.ModelForm):
    class Meta:
        model = RentPayment
        fields = ['status','reason','notify_tenant']

class StartWaterBillingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StartWaterBillingForm, self).__init__(*args, **kwargs)
        self.fields['total'].disabled = True
        self.fields['cleared'].disabled = True
        self.fields['units'].disabled = True
    class Meta:
        model = WaterBilling
        fields = ['units', 'unit_price', 'total', 'month','from_date', 'to_date','due_date', 'cleared', 'remarks']
        widgets = {
            'from_date': DateInput(),
            'to_date': DateInput(),
            'due_date': DateInput(),
        }

class WaterReadingForm(forms.ModelForm):
    class Meta:
        model = WaterConsumption
        fields = ['previous_reading','current_reading','reading_added']
        widgets = {
            'reading_added': DateInput(),
        }
        
class WaterBillUpdateForm(forms.ModelForm):
    class Meta:
        model = WaterBilling
        exclude = ['updated',]
        widgets = {
            'from_date': DateInput(),
            'to_date': DateInput(),
            'due_date': DateInput(),
        }

class WaterBillPaymentsForm(forms.ModelForm):
    class Meta:
        model = WaterPayments
        fields = ['payment_code','amount','payment_method','date_paid']
        widgets = {
            'date_paid': DateInput(),
        }
class UpdateWaterPaymentForm(forms.ModelForm):
    class Meta:
        model = WaterPayments
        exclude = ['created','updated']

class StartEBillCycleForm(forms.ModelForm):
    class Meta:
        model = ElectricityBilling
        fields = ['unit_price','measuring_unit','month',
                  'from_date','to_date','due_date','units','remarks']
        widgets = {
            'from_date': DateInput(),
            'to_date': DateInput(),
            'due_date': DateInput(),
        }
    def __init__(self, *args, **kwargs):
        super(StartEBillCycleForm, self).__init__(*args, **kwargs)
        self.fields['units'].disabled = True
        
class BillCycleUpdateForm(forms.ModelForm):
    class Meta:
        model = ElectricityBilling
        exclude = ['updated',]
        
        
class ElectricityReadingForm(forms.ModelForm):
    class Meta:
        model = ElectricityReadings
        fields = ['previous_reading','current_reading','reading_date']
        widgets = {
            'reading_date': DateInput(),
        }
        
class ElectricityPaySubmitForm(forms.ModelForm):
    class Meta:
        model = ElectricityPayments
        fields = ['payment_code','amount','payment_method','payment_date','remarks']
class UpdateElectricityPayForm(forms.ModelForm):
    class Meta:
        model = ElectricityPayments
        exclude = ['created','updated']
        
class NewWaterMeterForm(forms.ModelForm):
    def __init__(self, building, *args, **kwargs):
        super(NewWaterMeterForm,self).__init__(*args, **kwargs)
        self.fields['unit'].queryset = RentalUnit.objects.filter(building=building,water_meters=None)
    class Meta:
        model = WaterMeter
        fields = ['number', 'ssid', 'unit']
        
class NewElectricityMeterForm(forms.ModelForm):
    def __init__(self, building, *args, **kwargs):
        super(NewElectricityMeterForm,self).__init__(*args, **kwargs)
        self.fields['unit'].queryset = RentalUnit.objects.filter(building=building,electricity_meters=None)
    class Meta:
        model = ElectricityMeter
        fields = ['number', 'ssid', 'unit']