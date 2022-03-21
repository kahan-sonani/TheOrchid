import json

from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect

from app.models import ChannelName, CallLog
from landing.models import OUser


@login_required
def home(request):
    return render(request, 'home.html')


def logout_user(request):
    logout(request)
    return redirect('index')


@login_required
def contacts(request):
    return render(request, 'contacts.html')


@login_required
def profile(request):
    if request.method == 'POST':
        request.user.fname = request.POST.get('fname')
        request.user.lname = request.POST.get('lname')
        request.user.email = request.POST.get('email')
        request.user.save()
        messages.success(request, 'Profile updated successfully!')
    return render(request, 'Profile.html', {"user": request.user})


@login_required
def video_call(request):
    return render(request, 'video_call.html')


@login_required
def call_request(request):
    response = {}
    phone = None
    if request.method == 'POST':
        phone = reformat_phone(request.POST.get('phone'))
        try:
            user = OUser.objects.get(mobileno=phone)
            channel = ChannelName.objects.get(phone=user.mobileno)
            response['code'] = '3'
            response['channel_name'] = channel.channel_name
            response['caller_phone'] = request.user.mobileno
            response['caller_fname'] = request.user.fname
            response['caller_lname'] = request.user.lname
            log = CallLog.objects.create(caller=request.user, callee=user)
            log.save()

        except OUser.DoesNotExist or ChannelName.DoesNotExist:
            response['error'] = f'User with {phone} does not exists'
    return HttpResponse(json.dumps(response), content_type='application/json')


def reformat_phone(phone):
    return phone.replace('+91', '').replace(' ', '')


def save_channel(request):
    response = {}
    if request.method == 'POST':
        phone = request.user.mobileno
        channel_name = request.POST.get('channel_name')
        try:
            channel = ChannelName.objects.get(phone=phone)
            channel.channel_name = channel_name
            channel.save()
            response['result'] = 'Updated existing entry'
        except ChannelName.DoesNotExist:
            response['result'] = 'Saved the new entry'
            channel = ChannelName.objects.create(phone=phone, channel_name=channel_name)
            channel.save()

    return HttpResponse(json.dumps(response), content_type='application/json')


def call_timeout(request):
    response = {}
    if request.method == 'POST':
        code = request.POST.get('code')
        response['caller_phone'] = request.user.mobileno
        log = CallLog.objects.filter(caller=request.user).order_by('-time')[0]
        channel = ChannelName.objects.get(phone=log.callee.mobileno)
        response['channel_name'] = channel.channel_name
        response['code'] = code
    return HttpResponse(json.dumps(response), content_type='application/json')


def call_log(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q == '':
            logs = CallLog.objects.filter(Q(caller=request.user) | Q(callee=request.user)).order_by('-time')
        else:
            logs = CallLog.objects.filter(callee__fname__icontains=q).order_by('-time')
    else:
        logs = CallLog.objects.filter(Q(caller=request.user) | Q(callee=request.user)).order_by('-time')
    size = logs.count()
    paginator = Paginator(logs, 8)
    page_number = request.GET.get('page', 1)
    logs = paginator.get_page(page_number)
    return render(request, 'call_log.html', {'page_obj': logs, 'size': size})
