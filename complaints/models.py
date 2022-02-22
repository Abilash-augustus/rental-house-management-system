import string
from datetime import datetime
import random
from accounts.models import Tenants
from django.db import models
from rental_property.models import RentalUnit
from django.utils.text import slugify
from rental_property.models import Building

def get_report_image_path(instance, filename):
    user = instance.unit_report.reported_by.associated_account.username
    unit = instance.unit_report.unit.unit_number
    return "unit-images/{0}/{1}/{2}".format(user, unit, filename)

class UnitReportType(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30, unique=True, null=True, blank=True, help_text='Field generated automatically')
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            super(UnitReportType, self).save(*args, **kwargs)
        super(UnitReportType, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        verbose_name_plural = 'Report Types'

class UnitReport(models.Model):
    STATUS_CHOICES = (
        ('rc', 'Received'),
        ('pr', 'Processing'),
        ('rs', 'Resolved'),
        ('dr', 'Dropped'),
    )
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    reported_by = models.ForeignKey(Tenants, on_delete=models.DO_NOTHING)
    unit = models.ForeignKey(RentalUnit, on_delete=models.DO_NOTHING)
    report_type = models.ForeignKey(UnitReportType, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=5, choices=STATUS_CHOICES, default='rr')
    desc = models.TextField(verbose_name="Describe the situation", max_length=255)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.ascii_lowercase+string.digits + string.ascii_uppercase, k=7))
        if self.status == 'rc':
            RentalUnit.objects.filter(pk=self.unit_id).update(maintanance_status='nm')
        elif self.status == 'rs':
            RentalUnit.objects.filter(pk=self.unit_id).update(maintanance_status='op')
        else:
            RentalUnit.objects.filter(pk=self.unit_id).update(maintanance_status='ip')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reported_by} - {self.report_type}"

    class Meta:
        verbose_name_plural = 'Reports By Tenants'

class UnitReportAlbum(models.Model):
    unit_report = models.ForeignKey(UnitReport, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_report_image_path, width_field='image_width', height_field='image_height')
    image_width = models.IntegerField(default=600)
    image_height = models.IntegerField(default=500)

    def __str__(self):
        return f"Report on {self.unit_report.unit.unit_number} by {self.unit_report.reported_by}"

# TODO: Create notices, evacution notice e.t.c
class Complaints(models.Model):
    STATUS_CHOICES = [
        ('rc', 'Received'),
        ('rs', 'Resolved'),
    ]
    complaint_code = models.CharField(max_length=15, unique=True, blank=True, null=True)
    name = models.CharField(max_length=60, default="anonymous", help_text='Ignore field for an anonymous complaint')
    body = models.TextField(max_length=2000, verbose_name='Content')
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    status = models.CharField(max_length=5, choices=STATUS_CHOICES, default='rc')
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.complaint_code:
            self.complaint_code = ''.join(random.choices(string.ascii_lowercase+string.digits, k=10))

    def __str__(self):
        return f"{self.complaint_title[:10]}"

    class Meta:
        verbose_name_plural = 'Complaints'