import django.contrib.auth
import pyotp
import requests
import json

from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from datetime import datetime

import base64

from rest_framework.response import Response
from rest_framework.views import APIView

from landing.models import Contact
from django.contrib import messages
from landing.models import OUser


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
        user = authenticate(email=email, password=password)
        if user is not None:
            django.contrib.auth.login(request, user)
            return redirect('home')
        else:
            messages.warning(request, 'Invalid Credentials or User does not exists!')
    return render(request, 'Login.html')


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = OUser.objects.get(email=email)
            messages.warning(request, 'User already exists with given email id')
            return render(request, 'Register.html')
        except OUser.DoesNotExist:
            password = request.POST.get('password')
            firstname = request.POST.get('fname')
            lastname = request.POST.get('lname')
            phone = request.POST.get('phone')

            user = OUser.objects.create_user(
                email=email,
                password=password,
                fname=firstname,
                lname=lastname,
                mobileno=phone
            )
            user.save()
            messages.success(request, 'Registration Successful!')
    return render(request, 'Register.html')


class GenerateKey:
    @staticmethod
    def return_value(phone):
        return str(phone) + str(datetime.date(datetime.now())) + "Some Random Secret Key"


class GetPhoneNumberRegistered(APIView):
    # Get to Create a call for OTP
    @staticmethod
    def get(request, phone):
        if request.method == 'POST':
            try:
                mobile = OUser.objects.get(mobileno=phone)
            except ObjectDoesNotExist:
                email = request.POST.get('email')
                password = request.POST.get('password')
                firstname = request.POST.get('fname')
                lastname = request.POST.get('lname')
                user = OUser.objects.create_user(
                    email=email,
                    password=password,
                    fname=firstname,
                    lname=lastname,
                    mobileno=phone
                )

                mobile = OUser.objects.get(Mobile=phone)

            mobile.counter += 1  # Update Counter At every Call
            mobile.save()  # Save the data
            keygen = GenerateKey()
            key = base64.b32encode(keygen.return_value(phone).encode())  # Key is generated
            otp = pyotp.HOTP(key)  # HOTP Model for OTP is created
            print(otp.at(mobile.counter))
            # Using Multi-Threading send the OTP Using Messaging Services like Twilio or Fast2sms
            return Response({"OTP for mobile number verification for TheOrchid WebApp Registration": otp.at(mobile.counter)}, status=200)

    # This Method verifies the OTP
    @staticmethod
    def post(request, phone):
        try:
            mobile = OUser.objects.get(mobileno=phone)
        except ObjectDoesNotExist:
            return Response("User does not exist", status=404)  # False Call

        keygen = GenerateKey()
        key = base64.b32encode(keygen.return_value(phone).encode())  # Generating Key
        otp = pyotp.HOTP(key)  # HOTP Model
        if otp.verify(request.data["otp"], mobile.counter):  # Verifying the OTP
            mobile.isVerified = True
            mobile.save()
            return Response("You are authorised", status=200)
        return Response("OTP is wrong", status=400)
