import random
import string
from datetime import datetime

from accounts.models import Managers, Tenants
from django.db import models
from multiselectfield import MultiSelectField
from rental_property.models import RentalUnit

MONTHS_SELECT = [
    ('jan', 'January'),
    ('feb', 'February'),   
    ('mar', 'March'),        
    ('apr', 'April'),    
    ('may', 'May'),   
    ('jun', 'June'),       
    ('jul', 'July'),     
    ('aug', 'August'),  
     ('sep', 'September'),   
     ('oct', 'October'),    
     ('nov', 'November'), 
     ('dec', 'December'),
]
class UnitRentDetails(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Not Yet Paid'),
    ]
    tenant = models.ForeignKey(Tenants, on_delete=models.DO_NOTHING)
    unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE)
    rent_amount = models.DecimalField(max_digits=9, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=9, decimal_places=2)
    pay_for_month = MultiSelectField(choices=MONTHS_SELECT)
    paid_in_advance = models.BooleanField(default=False)
    amount_paid_in_advance = models.DecimalField(max_digits=9, decimal_places=2)
    cleared = models.BooleanField(default=False)
    due_date = models.DateTimeField()
    added = models.DateTimeField(default=datetime.now)
    updatd = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.amount_paid > self.rent_amount:
            self.cleared = True
            self.paid_in_advance = True
            self.amount_paid_in_advance = self.amount_paid-self.rent_amount
        elif self.rent_amount == self.amount_paid:
            self.cleared = True
        elif self.rent_amount > self.amount_paid:
            self.cleared = False
            super(UnitRentDetails, self).save(*args, **kwargs)
        super(UnitRentDetails, self).save(*args, **kwargs)
        
    
class RentPayment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    ]
    rent_details = models.ForeignKey(UnitRentDetails, on_delete=models.DO_NOTHING)
    tracking_code = models.CharField(max_length=15, unique=True, null=True, blank=True)
    payment_code = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    tenant = models.ForeignKey(Tenants, on_delete=models.DO_NOTHING)
    tracking_manager = models.ForeignKey(Managers, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)
    fully_paid = models.BooleanField(default=False)
    added_on = models.DateTimeField(default=datetime.now)
    updatd = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = ''.join(random.choices(string.digits, k=10))
            super(RentPayment, self).save(*args, **kwargs)
        super(RentPayment, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.tenant}"
