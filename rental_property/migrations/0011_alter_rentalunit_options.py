# Generated by Django 4.0.2 on 2022-03-15 22:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rental_property', '0010_alter_rentalunit_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rentalunit',
            options={'verbose_name_plural': 'Rental Houses'},
        ),
    ]
