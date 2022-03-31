from django import forms
from accounts.models import Tenants
from django_summernote.widgets import SummernoteWidget
from phonenumber_field.formfields import PhoneNumberField
from rental_property.models import RentalUnit

from utils.models import (ElectricityBilling, ElectricityMeter,
                              ElectricityPayments, ElectricityReadings,
                              RentIncrementNotice, RentPayment,
                              UnitRentDetails, WaterBilling, WaterConsumption,
                              WaterMeter, WaterPayments)


class DateInput(forms.DateInput):
    input_type = 'date'
    
class AddRentDetailsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddRentDetailsForm, self).__init__(*args, **kwargs)
        self.fields['currency'].disabled = True
        self.fields['added'].disabled = True
    class Meta:
        model = UnitRentDetails
        fields = ['currency','amount_paid','pay_for_month','start_date',
                  'end_date','due_date','notify_tenant','added']
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
        self.fields['rent_amount'].disabled = True
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
        self.fields['units'].disabled = True
    class Meta:
        model = WaterBilling
        fields = ['units', 'unit_price', 'total', 'month','from_date', 'to_date','due_date',]
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
    def __init__(self, *args, **kwargs):
        super(WaterBillUpdateForm, self).__init__(*args, **kwargs)
        self.fields['added'].disabled = True
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
    def __init__(self, *args, **kwargs):
        super(UpdateWaterPaymentForm, self).__init__(*args, **kwargs)
        self.fields['date_paid'].disabled = True
        self.fields['parent'].disabled = True
        self.fields['tracking_code'].disabled = True
        self.fields['payment_code'].disabled = True

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
        
class ElectricityBillCycleUpdateForm(forms.ModelForm):
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
        widgets = {
            'payment_date': DateInput(),
        }
        
class UpdateElectricityPayForm(forms.ModelForm):
    class Meta:
        model = ElectricityPayments
        exclude = ['created','updated','tracking_code']
    def __init__(self, *args, **kwargs):
        super(UpdateElectricityPayForm, self).__init__(*args, **kwargs)
        self.fields['payment_code'].disabled = True
        self.fields['parent'].disabled = True
        self.fields['payment_method'].disabled = True
        self.fields['payment_date'].disabled = True
        
class NewWaterMeterForm(forms.ModelForm):
    def __init__(self, building, *args, **kwargs):
        super(NewWaterMeterForm,self).__init__(*args, **kwargs)
        self.fields['unit'].queryset = RentalUnit.objects.filter(building=building,water_meters=None)
    class Meta:
        model = WaterMeter
        fields = ['number', 'ssid', 'unit']
        
class WaterMeterUpdateForm(forms.ModelForm):
    def __init__(self, building, *args, **kwargs):
        super(WaterMeterUpdateForm,self).__init__(*args, **kwargs)
        self.fields['unit'].queryset = RentalUnit.objects.filter(building=building)
    class Meta:
        model = WaterMeter
        exclude = ['updated','created']
        
class NewElectricityMeterForm(forms.ModelForm):
    def __init__(self, building, *args, **kwargs):
        super(NewElectricityMeterForm,self).__init__(*args, **kwargs)
        self.fields['unit'].queryset = RentalUnit.objects.filter(building=building,electricity_meters=None)
    class Meta:
        model = ElectricityMeter
        fields = ['number', 'ssid', 'unit']
        
class ElectricityMeterUpdateForm(forms.ModelForm):
    def __init__(self, building, *args, **kwargs):
        super(WaterMeterUpdateForm,self).__init__(*args, **kwargs)
        self.fields['unit'].queryset = RentalUnit.objects.filter(building=building)
    class Meta:
        model = ElectricityMeter
        exclude = ['created', 'updated']
        
class RentIncreaseNoticeForm(forms.ModelForm):
    def __init__(self, building, *args, **kwargs):
        super(RentIncreaseNoticeForm,self).__init__(*args, **kwargs)
        self.fields['to_tenants'].queryset = Tenants.objects.filter(rented_unit__building=building)
    class Meta:
        model = RentIncrementNotice
        fields = ['to_tenants','notify_all','takes_effect_on','re','notice_detail']
        widgets = {
            'takes_effect_on': DateInput(),
            'notice_detail': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '400px'}}),
            }
