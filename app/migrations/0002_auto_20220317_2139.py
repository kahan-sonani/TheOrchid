# Generated by Django 3.2.12 on 2022-03-17 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calllog',
            name='incoming',
            field=models.BooleanField(blank=True),
        ),
        migrations.AlterField(
            model_name='calllog',
            name='missed',
            field=models.BooleanField(blank=True),
        ),
        migrations.AlterField(
            model_name='calllog',
            name='rejected',
            field=models.BooleanField(blank=True),
        ),
    ]