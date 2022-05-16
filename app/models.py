from django.db import models


# Create your models here.
from landing.models import OUser


class CallLog(models.Model):
    caller = models.ForeignKey(OUser, on_delete=models.CASCADE, related_name="caller", default=None)
    callee = models.ForeignKey(OUser, on_delete=models.CASCADE, related_name="callee", default=None)
    time = models.DateTimeField(auto_now=True)
    rejected = models.BooleanField(default=False)
    missed = models.BooleanField(default=False)


class CallSettings(models.Model):
    user = models.OneToOneField(OUser, on_delete=models.CASCADE, related_name="user", default=None, primary_key=True)
    enable_predictions = models.IntegerField(default=0)
    enable_transcriptions = models.IntegerField(default=0)

