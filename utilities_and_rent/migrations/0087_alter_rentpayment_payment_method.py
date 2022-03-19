# Generated by Django 4.0.2 on 2022-03-19 17:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utilities_and_rent', '0086_remove_stripepay_bill_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rentpayment',
            name='payment_method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='utilities_and_rent.paymentmethods'),
        ),
    ]
