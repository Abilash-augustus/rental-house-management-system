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
    name = models.CharField(max_length=30, help_text="mpesa, bank transfer e.g. kcb")
    account_name = models.CharField(max_length=50)
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
    notify_tenant = models.BooleanField(default=True)
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

               
class WaterBilling(models.Model):
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.DO_NOTHING)
    tenant = models.ForeignKey(Tenants, on_delete=models.DO_NOTHING)
    bill_code = models.CharField(max_length=15, unique=True, null=True, blank=True)
    meter_number = models.CharField(max_length=10)
    quantity = models.DecimalField(decimal_places=2, max_digits=9, default=0, null=True, blank=True)
    measuring_unit = models.CharField(max_length=20, default='Litres')
    unit_price = models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Unit Price (KES)')
    re_billed = models.DecimalField(decimal_places=2, max_digits=9, null=True, blank=True)
    total = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    month = MultiSelectField(choices=MONTHS_SELECT, null=True, blank=True)
    remarks = models.TextField(blank=True)
    cleared = models.BooleanField(default=False)    
    lock_cycle = models.BooleanField(default=False)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    added = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.bill_code:
            self.bill_code = ''.join(random.choices(string.ascii_lowercase, k=10))
        if self.quantity:
            self.total = self.quantity*self.unit_price
            super(WaterBilling, self).save(*args, **kwargs)
        super(WaterBilling, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.rental_unit} - {self.tenant}'
    
    class Meta:
        verbose_name_plural = 'Billing | Water Billing Cycles'
    
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
    parent = models.ForeignKey(WaterBilling, on_delete=models.DO_NOTHING)
    payment_code = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    payment_method = models.CharField(max_length=30,help_text="e.g. MPESA, KCB ...")
    date_paid = models.DateField()
    status = models.CharField(max_length=10, default='pending', choices=PAYMENT_STATUS_CHOICES)
    remarks = models.TextField(blank=True,null=True,max_length=155)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.payment_code}"
    
    class Meta:
        verbose_name = 'Billing | Water Bills Payments'
        verbose_name_plural = verbose_name
    
    
class ElectricityBilling(models.Model):
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.DO_NOTHING)
    tenant = models.ForeignKey(Tenants, on_delete=models.DO_NOTHING)
    bill_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    meter_id = models.CharField(max_length=20)
    measuring_unit = models.CharField(max_length=20, default='KWH')
    units = models.DecimalField(decimal_places=2, max_digits=9)
    unit_price = models.DecimalField(decimal_places=2, max_digits=9)
    total = models.DecimalField(decimal_places=2, max_digits=9, null=True, blank=True)
    month = MultiSelectField(choices=MONTHS_SELECT)
    remarks = models.TextField(blank=True)
    cleared = models.BooleanField(default=False)  
    lock_cycle = models.BooleanField(default=False)  
    from_date = models.DateField()
    to_date = models.DateField()
    due_date = models.DateField()
    added = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.bill_code:
            self.bill_code = ''.join(random.choices(string.ascii_letters+string.digits, k=12))
        if self.units:
            self.total = self.units*self.unit_price
            super(ElectricityBilling, self).save(*args, **kwargs)
        super(ElectricityBilling, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.rental_unit} - {self.tenant}'
    
    class Meta:
        verbose_name_plural = "Billing | Electricity Billing Cycles"
        
class ElectricityReadings(models.Model):
    parent = models.ForeignKey(ElectricityBilling, on_delete=models.CASCADE)
    previous_reading = models.DecimalField(decimal_places=2,max_digits=9)
    current_reading = models.DecimalField(decimal_places=2,max_digits=9)
    units = models.DecimalField(decimal_places=2,max_digits=9)
    reading_date = models.DateTimeField()
        
    
class ElectricityPayments(models.Model):
    parent = models.ForeignKey(ElectricityBilling, on_delete=models.DO_NOTHING)
    tracking_code = models.CharField(max_length=15, unique=True, null=True, blank=True)
    payment_code = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    payment_method = models.CharField(max_length=30, help_text="e.g. MPESA, KCB ...")
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    remarks = models.TextField(null=True, blank=True)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = ''.join(random.choices(string.digits+string.ascii_letters, k=10))
            super(ElectricityPayments, self).save(*args, **kwargs)
        super(ElectricityPayments, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Billing | Electricity Bill Payments'
        verbose_name_plural = verbose_name