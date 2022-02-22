from django import forms
from complaints.models import Complaints, UnitReport, UnitReportAlbum


class UnitReportForm(forms.ModelForm):
    class Meta:
        model = UnitReport
        fields = ['report_type', 'desc']

class UnitReportAlbumForm(forms.ModelForm):
    class Meta:
        model = UnitReportAlbum
        fields = ['image', ]
        
class ReportUpdateForm(forms.ModelForm):
    class Meta:
        model = UnitReport
        fields = ['status', ]