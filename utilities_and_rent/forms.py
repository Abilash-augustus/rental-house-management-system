from django import forms

from utilities_and_rent.models import (ElectricityBilling, ElectricityPayments,
                                       ElectricityReadings, RentPayment,
                                       UnitRentDetails, WaterBilling,
                                       WaterConsumption, WaterPayments)


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
        self.fields['rent_amount'].disabled = True
        self.fields['amount_paid'].disabled = True
        self.fields['pay_for_month'].disabled = True
        self.fields['paid_in_advance'].disabled = True
        self.fields['amount_paid_in_advance'].disabled = True
        self.fields['cleared'].disabled = True
        self.fields['start_date'].disabled = True
        self.fields['end_date'].disabled = True
        self.fields['added'].disabled = True
    class Meta:
        model = UnitRentDetails
        fields = ['currency','rent_amount','amount_paid','pay_for_month','paid_in_advance','amount_paid_in_advance',
                  'cleared','start_date','end_date','added','due_date','status','notify_tenant']
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
        self.fields['measuring_unit'].disabled = True
        self.fields['total'].disabled = True
        self.fields['cleared'].disabled = True
        self.fields['quantity'].disabled = True
    class Meta:
        model = WaterBilling
        fields = ['meter_number','quantity','measuring_unit', 'unit_price', 'total', 'from_date', 'to_date', 'cleared', 'remarks']
        widgets = {
            'from_date': DateInput(),
            'to_date': DateInput(),
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

class StartEBillCycleForm(forms.ModelForm):
    class Meta:
        model = ElectricityBilling
        fields = ['meter_id','measuring_unit','units','unit_price','month','remarks',
                  'from_date','to_date','due_date']
        widgets = {
            'from_date': DateInput(),
            'to_date': DateInput(),
            'due_date': DateInput(),
        }
        
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
        fields = ['payment_code','amount','payment_method','remarks']
