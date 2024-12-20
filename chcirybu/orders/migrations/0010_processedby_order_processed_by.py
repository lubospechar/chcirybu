# Generated by Django 5.1.4 on 2024-12-18 14:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0009_order_discount_percentage"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProcessedBy",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "processed_by",
                    models.CharField(max_length=30, verbose_name="Zpracovatel"),
                ),
            ],
            options={
                "verbose_name": "Odpovědnost za zpracování",
                "verbose_name_plural": "Odpovědnost za zpracování",
                "ordering": ["processed_by"],
            },
        ),
        migrations.AddField(
            model_name="order",
            name="processed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="orders.processedby",
            ),
        ),
    ]
