from rest_framework.authentication import BaseAuthentication

from apps.chat.helpers import authenticate_user_from_token


class AppIDPTokenAuthBackend(BaseAuthentication):
    """App IDP Token Authorization Backend."""

    def authenticate(self, request):
        """Authenticate user based on IDP / SSO token and return user"""

        auth_token = request.headers.get("Token", None)
        auth_host = request.headers.get("Issuer-Url", None)
        issuer = request.headers.get("Issuer", None)
        if auth_token:
            return authenticate_user_from_token(auth_token, auth_host, issuer)
        return None
