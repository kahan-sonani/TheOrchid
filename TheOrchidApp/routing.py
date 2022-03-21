import django.contrib.auth.backends
from channels.auth import AuthMiddlewareStack, AuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import re_path, path

from app.consumers import TOAConsumer

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'https': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path("ws/call", TOAConsumer.as_asgi()),
            ])
        )
    ),
})
