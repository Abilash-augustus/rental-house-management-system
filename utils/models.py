import random
import string
from datetime import datetime
from io import BytesIO

from accounts.models import Managers, Tenants
from config.settings import DEFAULT_FROM_EMAIL
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db import models
from django.core.validators import MinValueValidator
from django.template.loader import get_template
from multiselectfield import MultiSelectField
from rental_property.models import Building, RentalUnit
from xhtml2pdf import pisa
import pytz

User = get_user_model()

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
    name = models.CharField(
        max_length=30, help_text="mpesa, bank transfer e.g. kcb")
    account_name = models.CharField(max_length=50)
    paybill_number = models.CharField(
        max_length=20, null=True, blank=True, help_text='Not required for bank transfer')
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
        ('open', 'open'),
        ('closed', 'closed'),
        ('defaulted', 'Added To Defaulted'),
    ]
    RENT_TYPE_CHOICES = [
        ('rent', 'Monthly Rent'),
        ('s_deposit', 'Security Deposit'),
    ]
    code = models.CharField(max_length=15, unique=True, null=True, blank=True)
    tenant = models.ForeignKey(Tenants, on_delete=models.DO_NOTHING)
    unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE)
    rent_amount = models.DecimalField(
        max_digits=9, decimal_places=2, help_text="This field will be populated automatically")
    currency = models.CharField(max_length=10, default='KES')
    amount_paid = models.DecimalField(
        max_digits=9, decimal_places=2, default=0)
    pay_for_month = MultiSelectField(choices=MONTHS_SELECT)
    cleared = models.BooleanField(default=False)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='open')
    rent_type = models.CharField(
        max_length=15, choices=RENT_TYPE_CHOICES, default='rent')
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
            self.rent_amount = self.unit.rent_amount
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


class RentIncrementNotice(models.Model):
    ref_code = models.CharField(
        max_length=20, unique=True, null=True, blank=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    to_tenants = models.ManyToManyField(Tenants, blank=True)
    notify_all = models.BooleanField(
        default=True, verbose_name='Send TO All Tenants')
    re = models.CharField(
        max_length=155, default='Rent Increase', verbose_name="RE: ")
    takes_effect_on = models.DateField()
    notice_detail = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def receivers(self):
        return ', '.join([str(t.associated_account.username) for t in self.to_tenants.all()])

    def save(self, *args, **kwargs):
        if not self.ref_code:
            self.ref_code = ''.join(random.choices(string.digits, k=12))
            super(RentIncrementNotice, self).save(*args, **kwargs)
        super(RentIncrementNotice, self).save(*args, **kwargs)

    class meta:
        verbose_name = 'Rent Increment Notice'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.building.name} Rent Increase Notice"


PAYMENT_STATUS_CHOICES = [
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('pending', 'Pending'),
]


class RentPayment(models.Model):
    rent_details = models.ForeignKey(
        UnitRentDetails, on_delete=models.CASCADE, related_name='payment')
    tenant = models.ForeignKey(
        Tenants, on_delete=models.CASCADE, related_name='pay')
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, null=True, blank=True)
    manager = models.ForeignKey(Managers, on_delete=models.CASCADE,
                                null=True, blank=True, related_name='payments_manager')
    tracking_code = models.CharField(
        max_length=15, unique=True, null=True, blank=True)
    payment_code = models.CharField(max_length=155)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    paid_for_month = MultiSelectField(choices=MONTHS_SELECT)
    paid_on = models.DateField(null=True, blank=True)
    payment_method = models.ForeignKey(
        PaymentMethods, on_delete=models.CASCADE, null=True, blank=True)
    paid_with_stripe = models.BooleanField(default=False)
    status = models.CharField(
        max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')
    reason = models.TextField(
        verbose_name="Reason, if rejected", blank=True, null=True)
    confirmed = models.BooleanField(default=False)
    notify_tenant = models.BooleanField(default=False)
    added_on = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = ''.join(random.choices(string.digits, k=10))
        if self.status == 'approved':
            self.confirmed = True
        if not self.building:
            self.building = self.rent_details.unit.building
            super(RentPayment, self).save(*args, **kwargs)
        super(RentPayment, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant}"

    class Meta:
        verbose_name_plural = "Billing 1 | Rent Payments"


class WaterBilling(models.Model):
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenants, on_delete=models.CASCADE)
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, null=True, blank=True)
    bill_code = models.CharField(
        max_length=15, unique=True, null=True, blank=True)
    meter_number = models.ForeignKey('WaterMeter', on_delete=models.CASCADE)
    units = models.DecimalField(
        decimal_places=2, max_digits=9, default=0, null=True, blank=True)
    unit_price = models.DecimalField(
        decimal_places=2, max_digits=9, verbose_name='Unit Price (KES)',default=53.0)
    total = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    amount_paid = models.DecimalField(
        decimal_places=2, max_digits=9, default=0)
    month = MultiSelectField(choices=MONTHS_SELECT, null=True, blank=True)
    meter_rent = models.DecimalField(
        decimal_places=2, max_digits=9, default=50)
    remarks = models.TextField(blank=True, null=True)
    cleared = models.BooleanField(default=False)
    lock_cycle = models.BooleanField(default=False)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    added = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now_add=True)

    def amount_remaining(self):
        r_amount = self.total-self.amount_paid
        return r_amount

    def save(self, *args, **kwargs):
        if not self.bill_code:
            self.bill_code = ''.join(
                random.choices(string.ascii_lowercase, k=10))
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
    consumption = models.DecimalField(
        max_digits=9, decimal_places=2, default=0)
    reading_added = models.DateField()

    def save(self, *args, **kwargs):
        if self.current_reading:
            self.consumption = self.current_reading-self.previous_reading
            super(WaterConsumption, self).save(*args, **kwargs)
        super(WaterConsumption, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.reading_added}"


class WaterPayments(models.Model):
    parent = models.ForeignKey(WaterBilling, on_delete=models.CASCADE)
    tracking_code = models.CharField(
        max_length=15, unique=True, blank=True, null=True)
    payment_code = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    payment_method = models.CharField(
        max_length=30, help_text="e.g. MPESA, KCB ...")
    date_paid = models.DateField()
    status = models.CharField(
        max_length=10, default='pending', choices=PAYMENT_STATUS_CHOICES)
    remarks = models.TextField(
        blank=True, null=True, max_length=155, verbose_name="Message?")
    lock = models.BooleanField(default=False)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = ''.join(random.choices(
                string.ascii_letters+string.digits, k=10))
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
    bill_code = models.CharField(
        max_length=20, unique=True, null=True, blank=True)
    meter_id = models.ForeignKey('ElectricityMeter', on_delete=models.CASCADE)
    measuring_unit = models.CharField(max_length=20, default='KWH')
    units = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    unit_price = models.DecimalField(decimal_places=2, max_digits=9,default=24.18)
    total = models.DecimalField(
        decimal_places=2, max_digits=9, default=0, null=True, blank=True)
    amount_paid = models.DecimalField(
        decimal_places=2, max_digits=9, null=True, blank=True, default=0)
    month = MultiSelectField(choices=MONTHS_SELECT)
    remarks = models.TextField(blank=True, null=True)
    cleared = models.BooleanField(default=False)
    lock_cycle = models.BooleanField(default=False)
    from_date = models.DateField()
    to_date = models.DateField()
    due_date = models.DateField()
    added = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, null=True, blank=True)

    def remaining_amount(self):
        remaining = (self.total-self.amount_paid)
        return remaining

    def save(self, *args, **kwargs):
        if not self.bill_code:
            self.bill_code = ''.join(random.choices(
                string.ascii_letters+string.digits, k=12))
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
    previous_reading = models.DecimalField(decimal_places=2, max_digits=9)
    current_reading = models.DecimalField(decimal_places=2, max_digits=9)
    units = models.DecimalField(decimal_places=2, max_digits=9)
    reading_date = models.DateTimeField()


class ElectricityPayments(models.Model):
    parent = models.ForeignKey(ElectricityBilling, on_delete=models.CASCADE)
    tracking_code = models.CharField(
        max_length=15, unique=True, null=True, blank=True)
    payment_code = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    payment_method = models.CharField(
        max_length=30, help_text="e.g. MPESA, KCB ...")
    status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    remarks = models.TextField(null=True, blank=True, verbose_name="Message?")
    lock = models.BooleanField(default=False)
    payment_date = models.DateField()
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = ''.join(random.choices(
                string.digits+string.ascii_letters, k=10))
        if self.status == 'approved':
            self.lock = True
            super(ElectricityPayments, self).save(*args, **kwargs)
        super(ElectricityPayments, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Billing 3 | Electricity Bill Payments'
        verbose_name_plural = verbose_name

class WaterMeter(models.Model):
    number = models.CharField(max_length=20, unique=True)
    ssid = models.CharField(max_length=20, null=True, blank=True)
    unit = models.OneToOneField(
        RentalUnit, on_delete=models.CASCADE, related_name='water_meters')
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.number} - {self.unit}"


class ElectricityMeter(models.Model):
    number = models.CharField(max_length=20, unique=True)
    ssid = models.CharField(max_length=20, null=True, blank=True)
    unit = models.OneToOneField(
        RentalUnit, on_delete=models.CASCADE, related_name='electricity_meters')
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.number} - {self.unit}"
    

class MpesaOnline(models.Model):
    STATUS_OPTIONS = [
        ('recieved','Recieved'),
        ('updated', 'Updated'),
    ]
    tenant = models.ForeignKey(Tenants, on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey(UnitRentDetails, on_delete=models.CASCADE, null=True, blank=True)
    MerchantRequestID = models.CharField(max_length=155,null=True, blank=True)
    CheckoutRequestID = models.CharField(max_length=155, null=True, blank=True)
    ResultCode = models.CharField(max_length=100, null=True, blank=True)
    ResultDesc = models.CharField(max_length=100, null=True, blank=True)
    Amount = models.DecimalField(max_digits=9,decimal_places=2,null=True, blank=True)
    MpesaReceiptNumber = models.CharField(max_length=100, null=True, blank=True)
    TransactionDate = models.CharField(max_length=55, null=True, blank=True)    
    PhoneNumber = models.CharField(max_length=25, null=True, blank=True)
    update_status = models.CharField(max_length=10,choices=STATUS_OPTIONS,default='recieved')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.CheckoutRequestID}"

    class Meta:
        verbose_name = "Mpesa Online Payments"
        verbose_name_plural = verbose_name


class RentDefaulters(models.Model):
    DEFAULTED_STATUS_CHOICES = [
        ('active','Active'),
        ('cleared','Cleared'),
    ]
    site_account = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Associated Account')
    tenancy_account = models.ForeignKey(Tenants, on_delete=models.CASCADE,)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    defaulted_status = models.CharField(max_length=20,choices=DEFAULTED_STATUS_CHOICES,default='active')
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.site_account.username}"
    
    class Meta:
        verbose_name = 'Rent Defaulters'
        verbose_name_plural = verbose_name

class TemporaryRelief(models.Model):
    RELEIF_STATUS_CHOICES = [
        ('active','Active'),
        ('expired','Expired'),
    ]
    defaulter = models.ForeignKey(RentDefaulters, on_delete=models.CASCADE)
    relief_detail = models.TextField()
    status = models.CharField(max_length=10,default='active',choices=RELEIF_STATUS_CHOICES)
    expires = models.DateTimeField()
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    already_sent = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        utc = pytz.utc
        now = datetime.now().replace(tzinfo=utc)
        if self.already_sent == True: #TODO: update to compare time instead
            subject = "YOU HAVE BEEN GIVEN A TEMPORARY RELIEF EXPIRING {0}".format(self.expires)  
            text = "Please find the details in the attached file"   
            template = get_template('utilities_and_rent/mails/defaulter_relief.html')
            context = {'expires':self.expires,'detail':self.relief_detail,'status':self.status,'defaulter':self.defaulter}
            html = template.render(context)
            response = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), response)
            pdf = response.getvalue()
            filename = 'defaulted_rent_relief_{0}'.format(self.defaulter) + '.pdf'
            to_email = self.defaulter.site_account.email
            from_email = DEFAULT_FROM_EMAIL
            message = EmailMessage(subject, text, from_email, [to_email])
            message.attach(filename, pdf, "application/pdf")
            message.send(fail_silently=False)  
            self.already_sent = True
        if self.expires.replace(tzinfo=utc) < now:
            self.status = 'expired'
            super(TemporaryRelief, self).save(*args, **kwargs)
        super(TemporaryRelief, self).save(*args, **kwargs)
            
    
    def __unicode__(self):
        return self.defaulter
    
    