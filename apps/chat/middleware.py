from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from apps.chat.helpers import authenticate_user_from_token


@database_sync_to_async
def get_user(token, host=None, issuer=None):
    """Get the user from the database or return AnonymousUser."""

    return authenticate_user_from_token(token, host, issuer) or AnonymousUser()


class AppWSAuthMiddleware:
    """Custom Authentication Middleware"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        """Include User in scope based on custom authentication. Using IDP token to get & validate user."""

        request_data = dict(x.split("=") for x in scope["query_string"].decode().split("&"))
        try:
            idp_token = request_data.get("token")
        except [ValueError, KeyError]:
            idp_token = None
        try:
            host = request_data.get("issuer-url")
        except [ValueError, KeyError]:
            host = None
        try:
            issuer = request_data.get("issuer")
        except [ValueError, KeyError]:
            issuer = None
        scope["user"] = await get_user(idp_token, host, issuer)
        return await self.app(scope, receive, send)
