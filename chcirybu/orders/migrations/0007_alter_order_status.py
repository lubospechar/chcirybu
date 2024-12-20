# Generated by Django 5.1.4 on 2024-12-09 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0006_alter_order_phonenumber"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "formuář vyplněn"),
                    (1, "objednáno"),
                    (2, "připraveno"),
                    (3, "odeslána informační SMS"),
                    (4, "vyřízeno"),
                    (5, "odeslané platební údaje na email"),
                ],
                default=1,
            ),
        ),
    ]
