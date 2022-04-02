from django import forms
from accounts.models import Tenants
from django_summernote.widgets import SummernoteWidget

from core.models import Contact, ContactReply, EvictionNotice, ManagerTenantCommunication, ServiceRating, TenantEmails, UnitTour, MoveOutNotice


class DateInput(forms.DateInput):
    input_type = 'date'

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['full_name', 'email', 'subject', 'message']
        widgets = {
            "message": SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '400px'}}),
        }
class ContactReplyForm(forms.ModelForm):
    class Meta:
        model = ContactReply
        fields = ['message',]

class UnitTourForm(forms.ModelForm):
    class Meta:
        model = UnitTour
        fields = ['full_name', 'visitor_email', 'phone_number', 'visit_date', 'message']
        widgets = {
            'visit_date': DateInput(),
            'message': forms.Textarea,
        }

class VisitUpdateForm(forms.ModelForm):
    class Meta:
        model = UnitTour
        fields = ['full_name', 'visitor_email', 'phone_number', 'visit_date', 'message', 'visit_status',]
        widgets = {
            'full_name': forms.TextInput(attrs={'readonly':'readonly'}),
            'visitor_email': forms.EmailInput(attrs={'readonly':'readonly'}),
            'phone_number': forms.TextInput(attrs={'readonly':'readonly'}),
            'visit_date': DateInput(attrs={'readonly':'readonly'}),
            'message': forms.Textarea(attrs={'readonly':'readonly'}),    
        }

class EvictionNoticeForm(forms.ModelForm):
    def __init__(self, building, *args, **kwargs):
        super(EvictionNoticeForm,self).__init__(*args, **kwargs)
        self.fields['tenant'].queryset = Tenants.objects.filter(rented_unit__building=building)
    class Meta:
        model = EvictionNotice
        fields = ['tenant','notice_detail','eviction_status','eviction_due','send_email',]
        widgets = {
            'notice_detail': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '400px'}}),
            'eviction_due': DateInput(),
        }
        
class UpdateEvictionNotice(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateEvictionNotice, self).__init__(*args, **kwargs)
        self.fields['created'].disabled = True
    class Meta:
        model = EvictionNotice
        exclude = ['updated','building']
        widgets = {
            'eviction_due': DateInput(),
        }

class NewMoveOutNoticeForm(forms.ModelForm):
    class Meta:
        model = MoveOutNotice
        fields = ['move_out_date', 'reason', ]
        widgets = {
            'reason': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '700px'}}),
            'move_out_date': DateInput(),
        }
        
class CancelMoveOutForm(forms.ModelForm):
    class Meta:
        model = MoveOutNotice
        fields = ['drop',]
        
class UpdateMoveOutNotice(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateMoveOutNotice, self).__init__(*args, **kwargs)
        self.fields['code'].disabled = True
        self.fields['tenant'].disabled = True
        self.fields['move_out_date'].disabled = True
        self.fields['created'].disabled = True
        self.fields['drop'].disabled = True
    class Meta:
        model = MoveOutNotice
        exclude = ['updated','reason']
        
class ServiceRatingForm(forms.ModelForm):
    class Meta:
        model = ServiceRating
        exclude = ['updated','created','tenant','building']
        widgets = {
            'score': forms.NumberInput(attrs={
                'type': 'range','step': '1', 'min': '0', 'max': '5','id':'id_score'}),
            }
        
class NewTenantEmailForm(forms.ModelForm):
    class Meta:
        model = ManagerTenantCommunication
        fields = ['send_to_all','sent_to','subject','body']
        widgets = {
            'sent_to': forms.CheckboxSelectMultiple,
            'body': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '400px'}}),
        }
    def __init__(self, building, *args, **kwargs):
        super(NewTenantEmailForm, self).__init__(*args, **kwargs)
        self.fields['sent_to'].label = 'Receiers'
        self.fields['sent_to'].queryset = Tenants.objects.filter(rented_unit__building=building)
        
class FromTenantForm(forms.ModelForm):
    class Meta:
        model = TenantEmails
        fields = ['subject','content']
        widgets = {
            'content': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '400px'}}),
        }