from django.contrib import admin
from work_order.models import WorkOrder, HiredPersonnel, PersonnelContact

@admin.register(PersonnelContact)
class PersonnelContactAdmin(admin.ModelAdmin):
    list_display = ['personnel','subject','body','created']

@admin.register(HiredPersonnel)
class HiredPersonnelAdmin(admin.ModelAdmin):
    pass

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    pass