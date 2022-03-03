from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.forms import ModelForm
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
