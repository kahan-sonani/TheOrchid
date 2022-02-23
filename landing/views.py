import django.contrib.auth
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from datetime import datetime
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
