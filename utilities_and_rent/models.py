import random
import string
from datetime import datetime

from accounts.models import Managers, Tenants
from django.db import models
from multiselectfield import MultiSelectField
from rental_property.models import RentalUnit
from django.db.models.signals import post_save
from django.dispatch import receiver

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
class PaymentMethods(models.Model):
    name = models.CharField(max_length=30)
    paybill_number = models.CharField(max_length=20, null=True, blank=True, help_text='Not required for bank transfer')
    account_number = models.CharField(max_length=30)
    added = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name} - {self.account_number}'
    class Meta:
        verbose_name_plural = 'Payment Methods'
        
    
class UnitRentDetails(models.Model):
    STATUS_CHOICES = [
        ('payment_made', 'Payment Made'),
        ('no_payment', 'No Payment Made'),
    ]
    code = models.CharField(max_length=15, unique=True, null=True, blank=True)
    tenant = models.ForeignKey(Tenants, on_delete=models.DO_NOTHING)
    unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE)
    rent_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='KES')
    amount_paid = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pay_for_month = MultiSelectField(choices=MONTHS_SELECT)
    paid_in_advance = models.BooleanField(default=False)
    amount_paid_in_advance = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    cleared = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='no_payment')
    start_date = models.DateField()
    end_date = models.DateField()
    due_date = models.DateField()
    added = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def amount_remaining(self):
        r_amount = (self.rent_amount-self.amount_paid)
        return r_amount       
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.digits, k=12))
        if self.amount_paid > self.rent_amount:
            self.cleared = True
            if self.amount_paid-self.rent_amount > 0:
                self.paid_in_advance = True
                self.amount_paid_in_advance = self.amount_paid-self.rent_amount
        elif self.rent_amount == self.amount_paid:
            self.cleared = True
        elif self.rent_amount > self.amount_paid:
            self.cleared = False
            super(UnitRentDetails, self).save(*args, **kwargs)
        super(UnitRentDetails, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.tenant} - {self.pay_for_month} "
        
    class Meta:
        verbose_name_plural = 'Rent Details'
        verbose_name = 'Rent For Unit'
        

PAYMENT_STATUS_CHOICES = [
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('pending', 'Pending'),
    ]

class RentPayment(models.Model):
    rent_details = models.ForeignKey(UnitRentDetails, on_delete=models.DO_NOTHING)
    tenant = models.ForeignKey(Tenants, on_delete=models.DO_NOTHING)
    manager = models.ForeignKey(Managers, on_delete=models.CASCADE, null=True, blank=True)
    tracking_code = models.CharField(max_length=15, unique=True, null=True, blank=True)
    payment_code = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    paid_for_month = MultiSelectField(choices=MONTHS_SELECT)
    paid_on = models.DateField(null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethods, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    added_on = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    reason = models.TextField(help_text='If rejected...Reason..', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = ''.join(random.choices(string.digits, k=10))
            super(RentPayment, self).save(*args, **kwargs)
        super(RentPayment, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.tenant}"

               
class Water(models.Model):
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.DO_NOTHING)
    tenant = models.ForeignKey(Tenants, on_delete=models.DO_NOTHING)
    quantity = models.DecimalField(decimal_places=2, max_digits=9)
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(decimal_places=2, max_digits=9)
    total = models.DecimalField(decimal_places=2, max_digits=9)
    pay_for_month = MultiSelectField(choices=MONTHS_SELECT)
    remarks = models.TextField(blank=True)
    cleared = models.BooleanField(default=False)    
    from_date = models.DateField()
    to_date = models.DateField()
    due_date = models.DateField()
    
    def __str__(self):
        return f'{self.rental_unit} - {self.tenant}'
    
class WaterPayments(models.Model):
    utility = models.ForeignKey(Water, on_delete=models.DO_NOTHING)
    payment_code = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    payment_method = models.CharField(max_length=30)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    
class Electricity(models.Model):
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.DO_NOTHING)
    tenant = models.ForeignKey(Tenants, on_delete=models.DO_NOTHING)
    quantity = models.DecimalField(decimal_places=2, max_digits=9)
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(decimal_places=2, max_digits=9)
    total = models.DecimalField(decimal_places=2, max_digits=9)
    pay_for_month = MultiSelectField(choices=MONTHS_SELECT)
    remarks = models.TextField(blank=True)
    cleared = models.BooleanField(default=False)    
    from_date = models.DateField()
    to_date = models.DateField()
    due_date = models.DateField()
    
    def __str__(self):
        return f'{self.rental_unit} - {self.tenant}'
    
class ElectricityPayments(models.Model):
    utility = models.ForeignKey(Electricity, on_delete=models.DO_NOTHING)
    payment_code = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    payment_method = models.CharField(max_length=30)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    class Reading(models.Model):
        previous = models.CharField(max_length=20)