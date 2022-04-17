from django.contrib import admin

from core.models import (Contact, ContactReply, EvictionNotice, MoveOutNotice, ServiceRating,
                         UnitTour,ManagerTenantCommunication,TenantEmails)

class ContactReplyAdmin(admin.StackedInline):
    model = ContactReply
    
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'subject', 'created',]
    list_filter = ['created',]
    inlines = [ContactReplyAdmin,]

@admin.register(UnitTour)
class UnitTourAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'visitor_email', 'phone_number', 'visit_date', 'visit_status', 'created']
    list_filter = ['visit_date', ]

@admin.register(EvictionNotice)
class EvictionNoticeAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'unit', 'eviction_status', 'created']
    list_filter = ['eviction_status', 'created' ]

@admin.register(MoveOutNotice)
class VacateNoticeAdmin(admin.ModelAdmin):
    list_display = ['code','tenant', 'notice_status', 'move_out_date']

@admin.register(ServiceRating)
class ServiceRatingAdmin(admin.ModelAdmin):
    list_display = ['building','score','created','updated']
    list_filter = ['building','created',]

@admin.register(ManagerTenantCommunication)
class ManagerTenantCommunicationAdmin(admin.ModelAdmin):
    list_display = ['ref_number','subject','send_to_all','retract','created','updated']
    list_filter = ['building','send_to_all','created']
    search_fields = ['subject','ref_number']
    list_editable = ['retract',]

@admin.register(TenantEmails)
class TenantEmailsAdmin(admin.ModelAdmin):
    list_display = ['ref_number','subject','sent_by','created', 'updated']
    list_filter = ['building','created']
    search_fields = ['ref_number','subject',]