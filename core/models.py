import datetime
import random
import string

from accounts.models import Managers, Tenants
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError, models
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from rental_property.models import RentalUnit

User = get_user_model()

def get_pic_path(instance, filename):
    return 'user-docs/{0}/{1}'.format(instance.user.username, filename)


class Contact(models.Model):
    full_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Name: {self.full_name} | Email: {self.email}"

    class Meta:
        verbose_name_plural = 'Recieved Contacts'
        


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
    visit_status = models.CharField(choices=VISIT_STATUS_CHOICES, default='waiting', max_length=10)
    last_updated_by = models.ForeignKey(Managers, on_delete=models.DO_NOTHING, null=True, blank=True)
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.visit_code:
            self.visit_code = ''.join(random.choices(string.ascii_lowercase+string.digits + string.ascii_uppercase, k=12))
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
    tenant = models.OneToOneField(Tenants, on_delete=models.DO_NOTHING) #TODO: should i use foreignkey?
    move_out_date = models.DateField()
    reason = models.TextField(max_length=2000)
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
        verbose_name = "Tenant's Notices To Move Out"
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
    notice_detail = models.TextField(max_length=2000)
    eviction_due = models.DateTimeField()
    sent_by = models.ForeignKey(Managers, on_delete=models.DO_NOTHING)
    help_contact_phone = models.CharField(max_length=14)
    help_contact_email = models.EmailField(max_length=50)
    eviction_status = models.CharField(max_length=10, default='initiated', choices=NOTICE_STATUS_CHOICES)
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(auto_now=True)

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
    message = models.TextField(max_length=100)
    score = models.IntegerField(default=0,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(0)
        ],verbose_name="Rate us on a scale of 1 to 10", null=True, blank=True)
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.pk}"
