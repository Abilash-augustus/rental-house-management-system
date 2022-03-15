from django import forms
from complaints.models import Complaints, UnitReport, UnitReportAlbum
from django_summernote.widgets import SummernoteWidget

class UnitReportForm(forms.ModelForm):
    class Meta:
        model = UnitReport
        fields = ['report_type', 'other', 'desc']
        widgets = {
            'desc': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '550px'}}),
        }

class UnitReportAlbumForm(forms.ModelForm):
    class Meta:
        model = UnitReportAlbum
        fields = ['image', ]
        
class ReportUpdateForm(forms.ModelForm):
    class Meta:
        model = UnitReport
        fields = ['status', ]
        
class NewComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaints
        fields = ['name', 'body']
        widgets = {
            'body': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '600px'}}),
        }
        
class UpdateComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaints
        fields = ['status',]