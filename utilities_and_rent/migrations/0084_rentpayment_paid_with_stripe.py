# Generated by Django 4.0.2 on 2022-03-19 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities_and_rent', '0083_alter_unitrentdetails_rent_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='rentpayment',
            name='paid_with_stripe',
            field=models.BooleanField(default=False),
        ),
    ]
