# Generated by Django 4.1.1 on 2023-01-06 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_comment_doctor_comment_hospital_comment_sent_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='sent_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]