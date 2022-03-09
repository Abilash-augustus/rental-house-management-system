from django.contrib import admin

from core.models import (Contact, EvictionNotice, MoveOutNotice, ServiceRating,
                         UnitTour)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'subject', 'created',]
    list_filter = ['created',]

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
    pass