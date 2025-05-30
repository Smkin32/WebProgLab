
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import jokes.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            jokes.routing.websocket_urlpatterns
        )
    ),
})
