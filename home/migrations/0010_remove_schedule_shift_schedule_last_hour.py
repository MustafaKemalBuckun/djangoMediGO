# Generated by Django 4.1.1 on 2023-01-07 16:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_alter_schedule_shift'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='shift',
        ),
        migrations.AddField(
            model_name='schedule',
            name='last_hour',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='home.times'),
        ),
    ]
