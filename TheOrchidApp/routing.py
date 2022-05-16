from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path, path

from app.call_consumers import TOAConsumer

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'https': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
                URLRouter([
                    path("ws/call/<str:phone>", TOAConsumer.as_asgi()),
                ])
    ),
})
