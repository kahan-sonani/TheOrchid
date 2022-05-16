import gc
import json
import multiprocessing
import random

import numpy as np
import torch
from agora_token_builder import RtcTokenBuilder
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import time
from app.models import CallLog, CallSettings
from landing.models import OUser
from ml_model.configs import TransformerConfig
from ml_model.models import Transformer
from ml_model.utils import load_label_map, inference, KeypointsDataset, get_pt_model_uri
from torch.utils import data

label_map = load_label_map()
label_map = dict(zip(label_map.values(), label_map.keys()))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
config = TransformerConfig(size="large", max_position_embeddings=256)
model = Transformer(config=config, n_classes=263)
model = model.to(device)
pretrained_model_name = get_pt_model_uri()
ckpt = torch.load(pretrained_model_name)
model.load_state_dict(ckpt["model"])


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
    call_settings = {}
    try:
        user_settings = CallSettings.objects.get(user=request.user)
        call_settings['enable_predictions'] = user_settings.enable_predictions
        call_settings['enable_transcription'] = user_settings.enable_transcriptions

    except CallSettings.DoesNotExist:
        call_settings['enable_transcription'] = 0
        call_settings['enable_predictions'] = 0
    return render(request, 'video_call.html', context=call_settings)


@login_required
def call_request(request):
    response = {}
    phone = None
    if request.method == 'POST':
        phone = reformat_phone(request.POST.get('phone'))
        try:
            user = OUser.objects.get(mobileno=phone)
            response['code'] = '3'
            response['caller_phone'] = request.user.mobileno
            response['callee_phone'] = user.mobileno
            response['caller_fname'] = request.user.fname
            response['callee_lname'] = request.user.lname
            log = CallLog.objects.create(caller=request.user, callee=user)
            log.save()
        except OUser.DoesNotExist:
            response['error'] = f'User with {phone} does not exists'
    return HttpResponse(json.dumps(response), content_type='application/json')


def reformat_phone(phone):
    return phone.replace('+91', '').replace(' ', '')


def call_timeout(request):
    response = {}
    if request.method == 'POST':
        code = request.POST.get('code')
        response['caller_phone'] = request.user.mobileno
        log = CallLog.objects.filter(caller=request.user).order_by('-time')[0]
        response['callee_phone'] = log.callee.mobileno
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


def get_token_for_vc(request):
    appId = '3e7cba117dc14b9eb96d8d54c64f9294'
    appCertificate = '8d74a4ff4248452bb29361bdebfc3647'
    channelName = request.GET.get('channel')
    uid = random.randint(1, 230)
    expirationTimeInSeconds = 3600 * 24
    currentTimeStamp = time.time()
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName,
                                              uid, role, privilegeExpiredTs)
    log = CallLog.objects.filter(caller__mobileno=channelName).order_by('-time')[0]
    response = {
        'token': token,
        'uid': uid,
        'caller_phone': log.caller.mobileno,
        'callee_phone': log.callee.mobileno,
        'callee_fname': log.callee.fname,
        'caller_fname': log.caller.fname
    }
    return JsonResponse(response, safe=False)


def get_user(request):
    response = {
        'phone': request.user.mobileno,
        'fname': request.user.fname,
        'lname': request.user.lname
    }
    return JsonResponse(response, safe=False)


def enable_predictions(request):
    response = {}
    if request.method == 'POST':
        ep = int(request.POST.get('enable_predictions'))
        try:
            user = CallSettings.objects.get(user=request.user)
            user.enable_predictions = ep
            user.save()
        except CallSettings.DoesNotExist:
            new_user = CallSettings.objects.create(user=request.user)
            new_user.enable_predictions = ep
            new_user.save()
    response['result'] = 'Saved'
    return HttpResponse(json.dumps(response), content_type='application/json')


def enable_transcription(request):
    response = {}
    if request.method == 'POST':
        et = int(request.POST.get('enable_transcriptions'))
        try:
            user = CallSettings.objects.get(user=request.user)
            user.enable_transcriptions = et
            user.save()
        except CallSettings.DoesNotExist:
            new_user = CallSettings.objects.create(user=request.user)
            new_user.enable_transcriptions = et
            new_user.save()
    response['result'] = 'Saved'
    return HttpResponse(json.dumps(response), content_type='application/json')


async def model_inference(request):
    if request.method == 'POST':
        save_data = json.loads(request.POST.get('key_points'))
        save_data['pose_x'] = save_data['pose_x'] if save_data['pose_x'] else [[np.nan] * 25]
        save_data['pose_y'] = save_data['pose_y'] if save_data['pose_y'] else [[np.nan] * 25]
        save_data['hand1_x'] = save_data['hand1_x'] if save_data['hand1_x'] else [[np.nan] * 25]
        save_data['hand1_y'] = save_data['hand1_y'] if save_data['hand1_y'] else [[np.nan] * 25]
        save_data['hand2_x'] = save_data['hand2_x'] if save_data['hand2_x'] else [[np.nan] * 25]
        save_data['hand2_y'] = save_data['hand2_y'] if save_data['hand2_y'] else [[np.nan] * 25]

        dataset = KeypointsDataset(
            uid=save_data['uid'],
            key_points=save_data,
            max_frame_len=169,
        )
        dataloader = data.DataLoader(
            dataset,
            batch_size=1,
            shuffle=False,
            num_workers=4,
            pin_memory=True,
        )
        response = inference(dataloader=dataloader, model=model, label_map=label_map, device=device, uid=save_data['uid'])
        gc.collect()
        return HttpResponse(json.dumps(response), content_type='application/json')
