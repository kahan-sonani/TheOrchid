from __future__ import print_function

import os

from django.contrib import messages
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from landing.models import OUser

SCOPES = ['https://www.googleapis.com/auth/contacts']


@login_required
def home(request):
    return render(request, 'home.html')


def logout_user(request):
    logout(request)
    return redirect('index')


def contacts(request):

    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=SCOPES)
    creds = flow.run_local_server(port=0)
    return render(request, 'contacts.html')


def profile(request):

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user.save()
    user = request.user
    return render(request, 'Profile.html', {"user": user})


class ProfileForm(ModelForm):
    class Meta:
        model = OUser
        fields = ['fname', 'lname', 'email', 'mobileno', 'profile_photo']