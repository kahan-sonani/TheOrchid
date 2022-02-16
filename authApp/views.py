from django.shortcuts import render, HttpResponse


# Create your views here.
def login(request):
    return render(request, 'home.html')


def register(request):
    return HttpResponse('This is register page...')
