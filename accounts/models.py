from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image

def get_avatar_path(instance, filename):
    return 'user-avatar/{0}/{1}'.format(instance.username, filename)

def get_user_docs_path(instance, filename):
    return 'user-docs/{0}/{1}'.format(instance.associated_account, filename)

class User(AbstractUser):
    avatar = models.ImageField(upload_to=get_avatar_path, default='no-avatar.png')
    is_verified = models.BooleanField(default=False)
    is_tenant = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} | {self.first_name} {self.last_name}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=14)
    street_address = models.CharField(max_length=30)
    county = models.CharField(max_length=30)
    country = models.CharField(max_length=30, default='Kenya')
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Managers(models.Model):
    VER_STATUS = [
    ('rv', 'Revoked'),
    ('pv', 'Pending Approval'),
    ('ap', 'Approved'),
    ]
    ID_WARNING = 'Must be a valid ID!'
    associated_account = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100, null=True, blank=True)
    id_back = models.ImageField(upload_to=get_user_docs_path, help_text=ID_WARNING)
    id_front = models.ImageField(upload_to=get_user_docs_path, help_text=ID_WARNING)
    added_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='added_by')
    active_phone_number = models.CharField(max_length=14)
    whatsapp_number = models.CharField(max_length=14)
    status = models.CharField(max_length=3, choices=VER_STATUS, default='pv')
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.status == 'ap':
            User.objects.filter(pk=self.associated_account.pk).update(is_manager=True, is_verified=True)
            Profile.objects.filter(user=self.associated_account.pk).update(phone=self.active_phone_number)
        else:
            User.objects.filter(pk=self.associated_account.pk).update(is_manager=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.associated_account.username}"

    class Meta:
        verbose_name_plural = 'Managers'

from rental_property.models import RentalUnit

class Tenants(models.Model):
    associated_account = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Associated account')
    full_name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=10)
    id_front = models.ImageField(upload_to=get_user_docs_path, blank=True)
    id_back = models.ImageField(upload_to=get_user_docs_path, blank=True)
    active_phone_number = models.CharField(max_length=14, null=True, blank=True)
    policy_agreement = models.BooleanField(default=False)
    rented_unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE, related_name="tenants", null=True, blank=True)
    moved_in = models.BooleanField(default=False)
    move_in_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.moved_in == True:
            User.objects.filter(pk=self.associated_account_id).update(is_tenant=True)
            if self.rented_unit:
                RentalUnit.objects.filter(pk=self.rented_unit_id).update(status='occupied')
        else:
            User.objects.filter(pk=self.associated_account_id).update(is_tenant=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.associated_account.username} -> Tenant on Unit {self.rented_unit}"

    class Meta:
        verbose_name_plural = 'Tenants'