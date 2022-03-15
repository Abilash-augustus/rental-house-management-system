from django import forms
from complaints.models import UnitReport

from work_order.models import HiredPersonnel, PersonnelContact, WorkOrder, WorkOrderPayments
from accounts.models import Managers
from django_summernote.widgets import SummernoteWidget

class DateInput(forms.DateInput):
    input_type = 'date'
    
class NewHiredPersonnelForm(forms.ModelForm):
    class Meta:
        model = HiredPersonnel
        fields = ['associated_account','full_name','id_number','job_title',
                  'personnel_email','phone_number','gender','hired_date']
        widgets = {
            'hired_date': DateInput(),
        }
        
class UpdatePersonnelForm(forms.ModelForm):
    class Meta:
        model = HiredPersonnel
        exclude = ['created','updated']
        widgets = {
            'hired_date': DateInput(),
        }
        
class PersonnelContactForm(forms.ModelForm):
    class Meta:
        model = PersonnelContact
        fields = ['subject','body']

class NewWorkOrderForm(forms.ModelForm):
    def __init__(self, building, *args, **kwargs):
        super(NewWorkOrderForm,self).__init__(*args, **kwargs)
        self.fields['parent_report'].queryset = UnitReport.objects.filter(unit__building=building)
        self.fields['additional_workers'].queryset = HiredPersonnel.objects.filter(building=building)

    class Meta:
        model = WorkOrder
        exclude = ['created','updated','building','work_order_code']
        widgets = {
            'due_date': DateInput(),
            'additional_workers': forms.CheckboxSelectMultiple,
        }
        
class WorkOrderUpdateForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        exclude = ['updated','created',]
        widgets = {
            'due_date': DateInput(),
        }

class WorkOrderPaymentsForm(forms.ModelForm):
    class Meta:
        model = WorkOrderPayments
        fields = ['payment_code','paid_to_name','paid_to_account','payment_method','amount','payment_date']
        widgets = {
            'payment_date': DateInput(),
        }

class PaymentUpdateForm(forms.ModelForm):
    class Meta:
        model = WorkOrderPayments
        exclude = ['updated','tracking_code','created']
        widgets = {
            'payment_date': DateInput(),
        }