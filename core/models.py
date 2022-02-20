import datetime
import random
import string

from accounts.models import Managers, Tenants
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import IntegrityError, models
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from rental_property.models import RentalUnit
from accounts.models import Tenants

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

class VacateNotice(models.Model):
    NOTICE_CHOICES = [
        ('dropped', 'Dropped'),
        ('Approved', 'Approved'),
        ('checking', 'Checking'),
    ]
    tenant = models.OneToOneField(Tenants, on_delete=models.DO_NOTHING)
    move_out_notice = models.DateField()
    reason = models.TextField(max_length=255)
    notice_status = models.CharField(max_length=10, choices=NOTICE_CHOICES)
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tenant}'s Vacate Notice"