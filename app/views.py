from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect


def home(request):
    return render(request, 'home.html')


def logout_user(request):
    logout(request)
    return redirect('index')
