from django.contrib import admin
from work_order.models import WorkOrder, HiredPersonnel, PersonnelContact, WorkOrderPayments

@admin.register(PersonnelContact)
class PersonnelContactAdmin(admin.ModelAdmin):
    list_display = ['personnel','subject','body','created']
    list_filter = ['created',]

@admin.register(HiredPersonnel)
class HiredPersonnelAdmin(admin.ModelAdmin):
    list_display = ['full_name','job_title','personnel_email','phone_number','is_active','created']
    list_filter = ['is_active','gender','building']
    list_editable = ['is_active',]
    
class WorkOrderPaymentsAdmin(admin.StackedInline):
    model = WorkOrderPayments
    extra = 0    

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['work_order_code','parent_report','work_order_code','title','status','due_date','email_personnel','created']
    list_editable = ['status',]
    inlines = [WorkOrderPaymentsAdmin]
    list_filter = ['due_date','building','status','created']
    search_fields = ['work_order_code','title','due_date']