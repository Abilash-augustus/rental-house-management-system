from django.contrib import admin

from core.models import Contact, UnitTour


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'subject', 'created',]
    list_filter = ['created',]

@admin.register(UnitTour)
class UnitTourAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'visitor_email', 'phone_number', 'visit_date', 'visit_status', 'created']
    list_filter = ['visit_date', ]
