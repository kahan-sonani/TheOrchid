# Generated by Django 3.2.12 on 2022-03-04 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0002_remove_ouser_profile_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='ouser',
            name='is_busy',
            field=models.BooleanField(default=True),
        ),
    ]
