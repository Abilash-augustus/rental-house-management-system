import random
import string
from datetime import datetime
import math
from accounts.models import Managers, Tenants
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from multiselectfield import MultiSelectField
from rental_property.models import RentalUnit,Building
import uuid

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
    name = models.CharField(max_length=30, help_text="mpesa, bank transfer e.g. kcb")
    account_name = models.CharField(max_length=50)
    paybill_number = models.CharField(max_length=20, null=True, blank=True, help_text='Not required for bank transfer')
    account_number = models.CharField(max_length=30)
    added = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name} - {self.account_number}'
    class Meta:
        verbose_name_plural = 'Payment Options'
        
    
class UnitRentDetails(models.Model):
    STATUS_CHOICES = [
        ('refunded', 'Refunded'),
        ('open','open'),
        ('closed','closed'),
        ('defaulted','Defaulted'),
    ]
    RENT_TYPE_CHOICES = [
        ('rent','Monthly Rent'),
        ('s_deposit','Security Deposit'),
    ]
    code = models.CharField(max_length=15, unique=True, null=True, blank=True)
    tenant = models.ForeignKey(Tenants, on_delete=models.DO_NOTHING)
    unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE)
    rent_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='KES')
    amount_paid = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pay_for_month = MultiSelectField(choices=MONTHS_SELECT)
    cleared = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    rent_type = models.CharField(max_length=15,choices=RENT_TYPE_CHOICES,default='rent')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    due_date = models.DateTimeField()
    notify_tenant = models.BooleanField(default=True)
    added = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    
    def amount_remaining(self):
        r_amount = (self.rent_amount-self.amount_paid)
        return r_amount
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.digits, k=12))
        if self.amount_paid >= self.rent_amount:
            self.cleared = True
            self.status = 'closed'
        elif self.rent_amount > self.amount_paid:
            self.cleared = False
            super(UnitRentDetails, self).save(*args, **kwargs)
        super(UnitRentDetails, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.tenant} - {self.pay_for_month} "
        
    class Meta:
        verbose_name_plural = 'Billing 1 | Rent Details'
        verbose_name = 'Rent For Unit'
        

PAYMENT_STATUS_CHOICES = [
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('pending', 'Pending'),
    ]

class RentPayment(models.Model):
    rent_details = models.ForeignKey(UnitRentDetails, on_delete=models.CASCADE, related_name='payment')
    tenant = models.ForeignKey(Tenants, on_delete=models.CASCADE, related_name='pay')
    manager = models.ForeignKey(Managers, on_delete=models.CASCADE, null=True, blank=True, related_name='payments_manager')
    tracking_code = models.CharField(max_length=15, unique=True, null=True, blank=True)
    payment_code = models.CharField(max_length=155)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    paid_for_month = MultiSelectField(choices=MONTHS_SELECT)
    paid_on = models.DateField(null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethods, on_delete=models.CASCADE, null=True, blank=True)
    paid_with_stripe = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')
    reason = models.TextField(verbose_name="Reason, if rejected", blank=True, null=True)
    confirmed = models.BooleanField(default=False)
    notify_tenant = models.BooleanField(default=False)
    added_on = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = ''.join(random.choices(string.digits, k=10))
        if self.status == 'approved':
            self.confirmed = True
            super(RentPayment, self).save(*args, **kwargs)
        super(RentPayment, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.tenant}"
    
    class Meta:
        verbose_name_plural = "Billing 1 | Rent Payments"

               
class WaterBilling(models.Model):
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenants, on_delete=models.CASCADE)
    bill_code = models.CharField(max_length=15, unique=True, null=True, blank=True)
    meter_number = models.ForeignKey('WaterMeter', on_delete=models.CASCADE)
    units = models.DecimalField(decimal_places=2, max_digits=9, default=0, null=True, blank=True)
    unit_price = models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Unit Price (KES)')
    total = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    amount_paid = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    month = MultiSelectField(choices=MONTHS_SELECT, null=True, blank=True)
    meter_rent = models.DecimalField(decimal_places=2, max_digits=9, default=50)
    remarks = models.TextField(blank=True,null=True)
    cleared = models.BooleanField(default=False)    
    lock_cycle = models.BooleanField(default=False)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    added = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now_add=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True)
    
    def amount_remaining(self):
        r_amount = self.total-self.amount_paid
        return r_amount
    
    def save(self, *args, **kwargs):
        if not self.bill_code:
            self.bill_code = ''.join(random.choices(string.ascii_lowercase, k=10))
        if self.units:
            self.total = (self.units*self.unit_price)+self.meter_rent
        if self.amount_paid != 0:
            if self.total <= self.amount_paid:
                self.cleared = True
            else:
                self.cleared = False
                # to easen report generation
        if not self.building:
            self.building = self.rental_unit.building            
            super(WaterBilling, self).save(*args, **kwargs)
        super(WaterBilling, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.rental_unit} - {self.tenant}'
    
    class Meta:
        verbose_name_plural = 'Billing 2 | Water Billing Cycles'
    
class WaterConsumption(models.Model):
    parent = models.ForeignKey(WaterBilling, on_delete=models.CASCADE)
    previous_reading = models.DecimalField(max_digits=9, decimal_places=2)
    current_reading = models.DecimalField(max_digits=9, decimal_places=2)
    consumption = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    reading_added = models.DateField()
    
    def save(self, *args, **kwargs):
        if self.current_reading:
            self.consumption = self.current_reading-self.previous_reading
            super(WaterConsumption,self).save(*args,**kwargs)
        super(WaterConsumption,self).save(*args,**kwargs)
    
    def __str__(self):
        return f"{self.reading_added}"
    
class WaterPayments(models.Model):
    parent = models.ForeignKey(WaterBilling, on_delete=models.CASCADE)
    tracking_code = models.CharField(max_length=15, unique=True, blank=True, null=True)
    payment_code = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    payment_method = models.CharField(max_length=30,help_text="e.g. MPESA, KCB ...")
    date_paid = models.DateField()
    status = models.CharField(max_length=10, default='pending', choices=PAYMENT_STATUS_CHOICES)
    remarks = models.TextField(blank=True,null=True,max_length=155,verbose_name="Message?")
    lock = models.BooleanField(default=False)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = ''.join(random.choices(string.ascii_letters+string.digits, k=10))
        if self.status == 'approved':
            self.lock = True
            super(WaterPayments, self).save(*args, **kwargs)
        super(WaterPayments, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.payment_code}"
    
    class Meta:
        verbose_name = 'Billing 2 | Water Billing Payments'
        verbose_name_plural = verbose_name
    
class ElectricityBilling(models.Model):
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenants, on_delete=models.CASCADE)
    bill_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    meter_id = models.ForeignKey('ElectricityMeter', on_delete=models.CASCADE)
    measuring_unit = models.CharField(max_length=20, default='KWH')
    units = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    unit_price = models.DecimalField(decimal_places=2, max_digits=9)
    total = models.DecimalField(decimal_places=2, max_digits=9, default=0, null=True, blank=True)
    amount_paid = models.DecimalField(decimal_places=2, max_digits=9, null=True, blank=True, default=0)
    month = MultiSelectField(choices=MONTHS_SELECT)
    remarks = models.TextField(blank=True,null=True)
    cleared = models.BooleanField(default=False)  
    lock_cycle = models.BooleanField(default=False)  
    from_date = models.DateField()
    to_date = models.DateField()
    due_date = models.DateField()
    added = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True)
    
    def remaining_amount(self):
        remaining = (self.total-self.amount_paid)
        return remaining
    
    def save(self, *args, **kwargs):
        if not self.bill_code:
            self.bill_code = ''.join(random.choices(string.ascii_letters+string.digits, k=12))
        if self.units:
            self.total = self.units*self.unit_price
        if self.amount_paid != 0:
            if self.total <= self.amount_paid:
                self.cleared = True
            elif self.total > self.amount_paid:
                self.cleared = False
            # to easen report generation
        if not self.building:
            self.building = self.rental_unit.building  
            super(ElectricityBilling, self).save(*args, **kwargs)
        super(ElectricityBilling, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.rental_unit} - {self.tenant}'
    
    class Meta:
        verbose_name_plural = "Billing 3 | Electricity Billing Cycles"
        
class ElectricityReadings(models.Model):
    parent = models.ForeignKey(ElectricityBilling, on_delete=models.CASCADE)
    previous_reading = models.DecimalField(decimal_places=2,max_digits=9)
    current_reading = models.DecimalField(decimal_places=2,max_digits=9)
    units = models.DecimalField(decimal_places=2,max_digits=9)
    reading_date = models.DateTimeField()
        
    
class ElectricityPayments(models.Model):
    parent = models.ForeignKey(ElectricityBilling, on_delete=models.CASCADE)
    tracking_code = models.CharField(max_length=15, unique=True, null=True, blank=True)
    payment_code = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    payment_method = models.CharField(max_length=30, help_text="e.g. MPESA, KCB ...")
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    remarks = models.TextField(null=True, blank=True,verbose_name="Message?")
    lock = models.BooleanField(default=False)
    payment_date = models.DateField()
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = ''.join(random.choices(string.digits+string.ascii_letters, k=10))
        if self.status == 'approved':
            self.lock = True
            super(ElectricityPayments, self).save(*args, **kwargs)
        super(ElectricityPayments, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Billing 3 | Electricity Bill Payments'
        verbose_name_plural = verbose_name
        
class WaterMeter(models.Model):
    number = models.CharField(max_length=20,unique=True)
    ssid = models.CharField(max_length=20,null=True,blank=True)
    unit = models.OneToOneField(RentalUnit, on_delete=models.CASCADE, related_name='water_meters')
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.number} - {self.unit}"
    

class ElectricityMeter(models.Model):
    number = models.CharField(max_length=20,unique=True)
    ssid = models.CharField(max_length=20, null=True, blank=True)
    unit = models.OneToOneField(RentalUnit, on_delete=models.CASCADE, related_name='electricity_meters')
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.number} - {self.unit}"
    
class PayOnlineMpesa(models.Model):
    paid_for = models.ForeignKey(UnitRentDetails, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100,null=True, blank=True)
    last_name = models.CharField(max_length=100,null=True, blank=True)
    middle_name = models.CharField(max_length=100,null=True, blank=True)
    transaction_id = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=25,null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    reference = models.CharField(max_length=55,null=True, blank=True)
    organization_balance = models.DecimalField(decimal_places=2, max_digits=9)
    type = models.CharField(max_length=55,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    timestamp = models.CharField(max_length=55,null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return f"{self.request_id}"
    
    class Meta:
        verbose_name = "Mpesa Online Payments"
        verbose_name_plural = verbose_name