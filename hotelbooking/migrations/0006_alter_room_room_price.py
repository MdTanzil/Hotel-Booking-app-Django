# Generated by Django 4.2.1 on 2024-09-26 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hotelbooking", "0005_guest_lead"),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="room_price",
            field=models.DecimalField(decimal_places=2, max_digits=11),
        ),
    ]