import json

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from landing.models import OUser


@login_required
def home(request):
    return render(request, 'home.html')


def logout_user(request):
    logout(request)
    return redirect('index')


def contacts(request):
    return render(request, 'contacts.html')


def profile(request):
    user = OUser.objects.get(mobileno=request.user.mobileno)
    if request.method == 'POST':
        user.fname = request.POST.get('fname')
        user.lname = request.POST.get('lname')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return render(request, 'Profile.html', {"user": user})
    return render(request, 'Profile.html', {"user": user})


def video_call(request):
    return render(request, 'video_call.html')


def call_request(request):
    if request.method == 'POST':
        response_data = {}
        phone = request.POST.get('phone')
        try:
            phone = reformat_phone(phone)
            user = OUser.objects.get(mobileno=phone)
            if user.is_busy:
                response_data['result'] = f'{phone} is busy with someone else'
                return HttpResponse(json.dumps(response_data), content_type='application/json')
            else:
                response_data['redirect'] = '/videoCall'
                return HttpResponse(json.dumps(response_data), content_type='application/json')
        except OUser.DoesNotExist:
            response_data['result'] = f'{phone} is not registered as a user'
            return HttpResponse(json.dumps(response_data), content_type='application/json')


def reformat_phone(phone):
    return phone.replace('+91', '').replace(' ', '')
