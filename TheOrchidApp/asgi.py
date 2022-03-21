import os

from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

import app.consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TheOrchidApp.settings')


