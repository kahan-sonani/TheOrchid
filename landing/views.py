import django.contrib.auth
import pyotp
import requests
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from datetime import datetime
import base64
from rest_framework.views import APIView

from landing.models import Contact
from django.contrib import messages
from landing.models import OUser

url = "https://www.fast2sms.com/dev/bulkV2"


# Create your views here.
def index(request):
    if request.user.is_anonymous:
        return render(request, 'index.html')
    else:
        return redirect('home')


def about(request):
    return render(request, 'About.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        desc = request.POST.get('message')
        contactEle = Contact(name=name, email=email, description=desc, date=datetime.today())
        contactEle.save()
        messages.success(request, "Thank you! Your message has been sent.")
    return render(request, 'Contact.html')


def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            OUser.objects.get(email=email)
        except OUser.DoesNotExist:
            messages.warning(request, 'User does not exists!')
        else:
            user = authenticate(email=email, password=password)
            if user is not None:
                django.contrib.auth.login(request, user)
                return redirect('home')
            else:
                messages.warning(request, 'Invalid Credentials!')
    return render(request, 'Login.html')


def register(request):
    if request.method == 'POST':
        try:
            OUser.objects.get(email=request.POST.get('email'))
            messages.warning(request, "User already exists!")
        except OUser.DoesNotExist:
            return get(request,
                       fname=request.POST.get('fname'),
                       lname=request.POST.get('lname'),
                       email=request.POST.get('email'),
                       phone=request.POST.get('phone'),
                       password=request.POST.get('password')
                       )
    return render(request, 'Register.html')


def get(request, fname, lname, email, phone, password):
    response = None
    mobile = None
    try:
        mobile = OUser.objects.get(email=email)
    except ObjectDoesNotExist:
        user = OUser.objects.create_user(
            email=email,
            password=password,
            fname=fname,
            lname=lname,
            mobileno=phone
        )
        mobile = OUser.objects.get(email=email)
    mobile.counter += 1  # Update Counter At every Call
    mobile.save()  # Save the data
    keygen = GenerateKey()
    key = base64.b32encode(keygen.return_value(phone).encode())  # Key is generated
    otp = pyotp.HOTP(key)  # HOTP Model for OTP is created
    print(otp.at(mobile.counter))
    querystring = {
        "authorization": "k13sAiIfKoOeMYXDWLF98RBCcTp2vqVrJutGS74glwQ6Hymzd5havlBuEyrAFxe3sgfHOSIm8GP1MJ09",
        "variables_values": otp.at(mobile.counter), "route": "otp",
        "numbers": mobile.mobileno}
    headers = {
        'cache-control': "no-cache"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)

    context = {
        'fname': '',
        'lname': '',
        'email': '',
        'phone': '',
        'password': '',
        'display': 'none'
    }
    if response is not None:
        context['fname'] = mobile.fname
        context['lname'] = mobile.lname
        context['email'] = mobile.email
        context['phone'] = mobile.mobileno
        context['password'] = mobile.password
        context['display'] = 'block'
    return render(request, 'Register.html', context)


def post(request):
    phone = None
    email = None
    mobile = None
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            mobile = OUser.objects.get(email=email)
        except ObjectDoesNotExist:
            messages.warning(request, 'User does not exists!')

        keygen = GenerateKey()
        key = base64.b32encode(keygen.return_value(mobile.mobileno).encode())  # Generating Key
        otp = pyotp.HOTP(key)  # HOTP Model
        otpp = f"{request.POST.get('1')}{request.POST.get('2')}{request.POST.get('3')}{request.POST.get('4')}{request.POST.get('5')}{request.POST.get('6')}"
        if otp.verify(otpp, mobile.counter):  # Verifying the OTP
            mobile.is_verified = True
            mobile.save()
            messages.success(request, 'OTP verified!')
        else:
            if not mobile.is_verified:
                mobile.delete()
            messages.warning(request, 'OTP you entered was wrong!')
    return render(request, 'Register.html', {'display': 'none'})


class GenerateKey:
    @staticmethod
    def return_value(phone):
        return str(phone) + str(datetime.date(datetime.now())) + "Some Random Secret Key"
