from django.contrib import admin

from complaints.models import (Complaints, HelpContacts, UnitReport,
                               UnitReportAlbum, UnitReportType)


class UnitReportAlbumAdmin(admin.StackedInline):
    model = UnitReportAlbum

@admin.register(UnitReport)
class UnitReportAdmin(admin.ModelAdmin):
    inlines = [UnitReportAlbumAdmin]
    list_display = ['reported_by', 'unit', 'report_type', 'status', 'created']
    list_filter = ['report_type', 'created', 'updated']


@admin.register(Complaints)
class ComplaintsAdmin(admin.ModelAdmin):
    list_display = ['complaint_code', 'name', 'status', 'created', 'updated']
    list_filter = ['status', 'created']

@admin.register(UnitReportType)
class UnitReportTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created', 'updated']
    
    
@admin.register(HelpContacts)
class HelpContactsAdmin(admin.ModelAdmin):
    list_display = ['contact','is_type','used_for','make_publicly_available','created']
    list_filter = ['is_type','created']
    list_editable = ['make_publicly_available']