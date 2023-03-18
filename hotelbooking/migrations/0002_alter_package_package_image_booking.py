# Generated by Django 4.1.7 on 2023-03-17 06:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotelbooking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='package_image',
            field=models.ImageField(upload_to=None, verbose_name='package'),
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(blank=True, default=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('guest_name', models.CharField(max_length=100)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotelbooking.room')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
