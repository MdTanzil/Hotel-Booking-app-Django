# Generated by Django 4.2.1 on 2024-09-26 16:30

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("hotelbooking", "0006_alter_room_room_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="room_desc",
            field=ckeditor.fields.RichTextField(),
        ),
    ]