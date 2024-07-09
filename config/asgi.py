import os
import sys
from pathlib import Path

import django

# This allows easy placement of apps within the interior
# apps directory.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(BASE_DIR / "apps"))

# If DJANGO_SETTINGS_MODULE is unset, default to the local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa
from django.core.asgi import get_asgi_application  # noqa

from apps.chat.middleware import AppWSAuthMiddleware  # noqa
from apps.chat.routing import websocket_urlpatterns  # noqa

# Import websocket application here, so apps from django_application are loaded first
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AppWSAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
