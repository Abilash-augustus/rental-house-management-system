from django import forms
from django_summernote.widgets import SummernoteWidget

from core.models import Contact, EvictionNotice, UnitTour


class DateInput(forms.DateInput):
    input_type = 'date'

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['full_name', 'email', 'subject', 'message']
        widgets = {
            "message": forms.Textarea(
                attrs={"placeholder": "Put your message here..."}
            ),
        }


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
    class Meta:
        model = EvictionNotice
        fields = ['notice_detail','help_contact_phone', 'help_contact_email', 'eviction_status']
        widgets = {
            'notice_detail': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '400px'}}),
        }