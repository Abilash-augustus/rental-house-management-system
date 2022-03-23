import random
from django.db import models
import string
from accounts.models import Managers
from datetime import datetime
from django.contrib.auth import get_user_model
from complaints.models import UnitReport
from rental_property.models import Building, RentalUnit

User = get_user_model()

class HiredPersonnel(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    associated_account = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    personnel_manager = models.ForeignKey(Managers, on_delete=models.CASCADE)
    personnel_code = models.CharField(max_length=9, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=55)
    personnel_email = models.EmailField(max_length=155)
    phone_number = models.CharField(max_length=15)
    id_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    hired_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.personnel_code:
            self.personnel_code = ''.join(random.choices(string.digits, k=6))
            super(HiredPersonnel, self).save(*args, **kwargs)
        super(HiredPersonnel, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} --> {self.job_title}"
    
class PersonnelContact(models.Model):
    personnel = models.ForeignKey(HiredPersonnel, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    body = models.TextField(max_length=255)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.personnel} {self.subject}"
    
    #TODO: Write contact for tenant
    
class WorkOrder(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [
        ('waiting', 'Waiting Assignment'),
        ('assigned', 'Assigned'),
        ('in-progress', 'In-Progress'),
        ('completed', 'Completed'),
    ]
    parent_report = models.ForeignKey(UnitReport, on_delete=models.CASCADE, null=True, blank=True,
                                      help_text="Leave blank for general work order")
    work_order_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    est_duration = models.CharField(max_length=70, help_text="e.g. 2 days")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    assigned_to = models.ForeignKey(HiredPersonnel, on_delete=models.CASCADE)
    additional_workers = models.ManyToManyField(HiredPersonnel, related_name='other_workers', blank=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES, default='waiting')
    due_date = models.DateField()
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    email_personnel = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.work_order_code:
            self.work_order_code = ''.join(random.choices(string.digits, k=10))
        if self.assigned_to:

            self.status = 'assigned'
            super(WorkOrder, self).save(*args, **kwargs)
        super(WorkOrder, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title}"
    

class WorkOrderPayments(models.Model):
    parent_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True)
    tracking_code = models.CharField(max_length=12, unique=True, null=True, blank=True)
    payment_code = models.CharField(max_length=30)
    paid_to_name = models.CharField(max_length=55)
    paid_to_account = models.CharField(max_length=55,null=True, blank=True)
    payment_method = models.CharField(max_length=30,help_text="e.g Mpesa")
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    payment_date = models.DateTimeField()
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = ''.join(random.choices(string.digits, k=10))
        if not self.building:
            self.building = self.parent_order.building
            super(WorkOrderPayments, self).save(*args, **kwargs)
        super(WorkOrderPayments, self).save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'Payments'
        verbose_name_plural = verbose_name
        
    
    def __str__(self):
        return f"{self.tracking_code}"