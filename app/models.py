from django.db import models


# Create your models here.
from landing.models import OUser


class CallLog(models.Model):
    caller = models.ForeignKey(OUser, on_delete=models.CASCADE, related_name="caller", default=None)
    callee = models.ForeignKey(OUser, on_delete=models.CASCADE, related_name="callee", default=None)
    time = models.DateTimeField(auto_now=True)
    rejected = models.BooleanField(default=False)
    missed = models.BooleanField(default=False)


class ChannelName(models.Model):
    phone = models.CharField(primary_key=True, max_length=10)
    channel_name = models.CharField(max_length=122)

