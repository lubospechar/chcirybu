# Generated by Django 5.1.4 on 2024-12-09 16:09

import phonenumber_field.modelfields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0005_alter_order_voucher"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="phonenumber",
            field=phonenumber_field.modelfields.PhoneNumberField(
                max_length=128, region="CZ", verbose_name="Telefon"
            ),
        ),
    ]
