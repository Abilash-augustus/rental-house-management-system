import datetime
import random
import string

from accounts.models import Managers, Tenants
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError, models
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from rental_property.models import Building, RentalUnit

User = get_user_model()

def get_pic_path(instance, filename):
    return 'user-docs/{0}/{1}'.format(instance.user.username, filename)


class Contact(models.Model):
    ref_code = models.CharField(max_length=15, unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    status = models.CharField(choices=[('open','Open'),('closed','Closed')],max_length=10,default='open')
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.ref_code:
            self.ref_code = ''.join(random.choices(string.digits, k=10))
            super(Contact, self).save(*args, **kwargs)
        super(Contact, self).save(*args, **kwargs)

    def __str__(self):
        return f"Name: {self.full_name} | Email: {self.email}"

    class Meta:
        verbose_name_plural = 'Received Contact'
        
class ContactReply(models.Model):
    parent = models.ForeignKey(Contact, on_delete=models.CASCADE)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
        


class UnitTour(models.Model):
    VISIT_STATUS_CHOICES = [
        ('cancelled', 'Cancelled'),
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('visited', 'Visited'),
    ]
    visit_code = models.CharField(max_length=15, unique=True, null=True, blank=True, help_text="Generated automaticall")
    full_name = models.CharField(max_length=20)
    visitor_email = models.EmailField(verbose_name='Email')
    phone_number = models.CharField(max_length=15)
    visit_date = models.DateField(validators=[MinValueValidator(datetime.date.today, message='Past dates are not allowed!')])
    message = models.TextField(null=True, blank=True)
    unit = models.ForeignKey(RentalUnit, on_delete=models.DO_NOTHING)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True)
    visit_status = models.CharField(choices=VISIT_STATUS_CHOICES, default='waiting', max_length=10)
    last_updated_by = models.ForeignKey(Managers, on_delete=models.DO_NOTHING, null=True, blank=True)
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.visit_code:
            self.visit_code = ''.join(random.choices(string.ascii_lowercase+string.digits + string.ascii_uppercase, k=12))
        if not self.building:
            self.building = self.unit.building
            super(UnitTour, self).save()
        super(UnitTour, self).save()

    def __str__(self):
        return f"{self.full_name} - {self.visitor_email}"

    class Meta:
        verbose_name_plural = 'Scheduled Visits'

class MoveOutNotice(models.Model):
    NOTICE_CHOICES = [
        ('received', 'Recieved'),
        ('dropped', 'Dropped'),
        ('confirmed', 'Confirmed'),
        ('checking', 'Checking'),
    ]
    code = models.CharField(max_length=15, blank=True, null=True)
    tenant = models.ForeignKey(Tenants, on_delete=models.DO_NOTHING)
    move_out_date = models.DateField()
    reason = models.TextField()
    notice_status = models.CharField(max_length=10, choices=NOTICE_CHOICES, default='received')
    drop = models.BooleanField(default=False, verbose_name='I would like to drop this notice')
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.digits, k=12))
            super(MoveOutNotice, self).save()
        super(MoveOutNotice, self).save()
    
    class Meta:
        verbose_name = "Tenant's To Move Out Notice"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.tenant}'s Vacate Notice"

class EvictionNotice(models.Model):
    NOTICE_STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('evicted', 'Evicted'),
        ('dropped', 'Dropped'),
    ]
    notice_code = models.CharField(max_length=10, blank=True, null=True, unique=True)
    tenant = models.OneToOneField(Tenants, on_delete=models.DO_NOTHING)
    unit = models.ForeignKey(RentalUnit, on_delete=models.DO_NOTHING)
    notice_detail = models.TextField()
    eviction_due = models.DateTimeField()
    sent_by = models.ForeignKey(Managers, on_delete=models.DO_NOTHING)
    eviction_status = models.CharField(max_length=10, default='initiated', choices=NOTICE_STATUS_CHOICES)
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(auto_now=True)
    send_email = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.notice_code:
            self.notice_code = ''.join(random.choices(string.digits, k=10))
            super(EvictionNotice, self).save()
        super(EvictionNotice, self).save()

        #TODO: update unit status to hold and rented unit for tenant

    def __str__(self):
        return f"{self.notice_code} | {self.tenant.associated_account.username}"
    
    
class ServiceRating(models.Model):    
    tenant = models.ForeignKey(Tenants, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField(max_length=100)
    score = models.IntegerField(default=0,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ],verbose_name="Rate us", null=True, blank=True)
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.building:
            self.building = self.tenant.rented_unit.building
            super(ServiceRating, self).save(*args, **kwargs)
        super(ServiceRating, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.pk}"

class ManagerTenantCommunication(models.Model):
    ref_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    sent_to = models.ManyToManyField(Tenants,blank=True)
    send_to_all = models.BooleanField(default=False)
    sent_by = models.ForeignKey(Managers, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    body = models.TextField()
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(auto_now=True)
    retract = models.BooleanField(default=False)
    
    def receiver_names(self):
        return ', '.join([str(t.associated_account.username) for t in self.sent_to.all()])
    
    def save(self, *args, **kwargs):
        if not self.ref_number:
            self.ref_number = ''.join(random.choices(string.digits, k=10))
            super(ManagerTenantCommunication, self).save(*args, **kwargs)
        super(ManagerTenantCommunication, self).save(*args, **kwargs)
    class Meta:
        verbose_name_plural = 'Archives | Manager E-Mails'
    def __Str__(self):
        return f"{self.sent_to}"
    
class TenantEmails(models.Model):
    ref_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    sent_to = models.ForeignKey(Managers, on_delete=models.CASCADE)
    sent_by = models.ForeignKey(Tenants, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    content = models.TextField()
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.ref_number:
            self.ref_number = ''.join(random.choices(string.digits, k=10))
            super(TenantEmails, self).save(*args, **kwargs)
        super(TenantEmails, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = 'Archives | E-mails From Tenants'
    def __str__(self):
        return f"{self.ref_number}"