from django.shortcuts import render
from datetime import datetime
from landing.models import Contact


# Create your views here.
def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'About.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        desc = request.POST.get('message')
        contactEle = Contact(name=name, email=email, description=desc, date=datetime.today())
        contactEle.save()
    return render(request, 'Contact.html')


def login(request):
    return render(request, 'Login.html')
