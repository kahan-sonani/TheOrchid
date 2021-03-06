# Generated by Django 3.2.12 on 2022-03-31 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('fname', models.CharField(max_length=122)),
                ('lname', models.CharField(max_length=122)),
                ('is_busy', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('counter', models.IntegerField(default=0)),
                ('email', models.EmailField(max_length=155)),
                ('mobileno', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True)),
                ('staff', models.BooleanField(default=False)),
                ('admin', models.BooleanField(default=False)),
                ('time_stamp', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=122)),
                ('email', models.CharField(max_length=122)),
                ('description', models.TextField()),
                ('date', models.DateField()),
            ],
        ),
    ]
