from django import forms

from utilities_and_rent.models import RentPayment, UnitRentDetails

class DateInput(forms.DateInput):
    input_type = 'date'

class SubmitPaymentsForm(forms.ModelForm):
    class Meta:
        model = RentPayment
        fields = ['payment_code', 'amount', 'payment_method', 'paid_on']   
        widgets = {
            'paid_on': DateInput(),
        } 