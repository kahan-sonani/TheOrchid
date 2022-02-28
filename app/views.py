from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
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