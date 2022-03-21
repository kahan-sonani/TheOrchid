# Generated by Django 3.2.12 on 2022-03-15 18:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelName',
            fields=[
                ('phone', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('channel_name', models.CharField(max_length=122)),
            ],
        ),
        migrations.CreateModel(
            name='CallLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now=True)),
                ('rejected', models.BooleanField()),
                ('incoming', models.BooleanField()),
                ('missed', models.BooleanField()),
                ('callee', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='callee', to=settings.AUTH_USER_MODEL)),
                ('caller', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='caller', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]