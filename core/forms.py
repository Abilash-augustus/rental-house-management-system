from django import forms

from core.models import Contact, UnitTour


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
