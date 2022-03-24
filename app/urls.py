"""TheOrchidApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('logout', views.logout_user, name='logout'),
    path('contacts', views.contacts, name='contacts'),
    path('profile', views.profile, name='profile'),
    path('call_log', views.call_log, name='call_log'),
    path('videoCall', views.video_call, name='video_call'),
    path('callRequest', views.call_request, name='call_request'),
    path('saveChannel', views.save_channel, name='save_channel'),
    path('callTimeout', views.call_timeout, name='call_timeout'),
    path('acceptCall', views.accept_call, name='accept_call'),
    path('get_token_for_vc/', views.get_token_for_vc, name='get_token_for_vc')
]

