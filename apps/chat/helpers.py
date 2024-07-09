import json

import jwt
import requests
from django.utils.translation import gettext_lazy as _
from jwt import PyJWKClient
from rest_framework.exceptions import AuthenticationFailed

from apps.chat.models import Tenant, User
from apps.common.idp_service import idp_get_request
from config.settings import IDP_CONFIG


def get_tenant_from_idp_data(data):
    """Return the Tenant obj. Get or create tenant."""

    try:
        tenant = Tenant.objects.get(tenant_id=data["id"])
    except Tenant.DoesNotExist:
        tenant = Tenant.objects.create(name=data["name"], tenant_id=data["id"])
    return tenant


def get_user_from_idp_data(data, tenant):
    """Return the User obj. Get or create user."""

    try:
        user = User.objects.get(user_id=data["id"])
    except User.DoesNotExist:
        user = User.objects.create_user(
            first_name=data["name"],
            last_name=data["surname"],
            email=data["emailAddress"],
            user_id=data["id"],
            tenant=tenant,
        )
    return user, None


def validate_keycloak_token(issuer_url, token):
    """Validate KC token."""

    # jwt verification options
    options = {
        "verify_signature": True,
        "require": ["exp", "iss"],
        "verify_exp": True,
        "verify_iss": True,
        "verify_aud": False,
    }
    # Verify the JWT token.
    try:
        import ssl

        jwks_endpoint = get_jwks_uri(issuer_url)
        # import urllib.request
        # For now disabling SSL certificate verification for testing
        """TO-DO-Need to get ssl certificate path here"""
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        jwks_client = PyJWKClient(uri=jwks_endpoint, cache_keys=True, lifespan=1200, ssl_context=ssl_context)
        jwk_set = jwks_client.get_jwk_set()
        jwk_key = jwk_set.keys[0]
        decoded_token = jwt.decode(
            jwt=token, key=jwk_key.key, algorithms=["RS256"], options=options, issuer=issuer_url
        )
        tenant_name = decoded_token["iss"].split("https://auth.techademy.com/realms/")[-1]
        user_name = decoded_token["name"].split(" ")
        tenant = get_tenant_from_idp_data(data={"id": decoded_token["B2B"], "name": tenant_name})
        user_data = {
            "name": decoded_token["given_name"],
            "surname": user_name[-1] if len(user_name) > 1 else None,
            "emailAddress": decoded_token["email"],
            "id": decoded_token["sub"],
        }
        return get_user_from_idp_data(user_data, tenant)
    except Exception:
        raise AuthenticationFailed(_("Key cloak authentication failed."))


def get_jwks_uri(issuer):
    openid_config_url = f"{issuer}/.well-known/openid-configuration"
    response = requests.get(openid_config_url, verify=False)
    data = json.loads(response.content)
    return data.get("jwks_uri")


def authenticate_user_from_token(token, host=None, issuer=None):
    """Authenticate user from IDP / SSO / KC token and return the user."""

    if issuer == "KC":
        return validate_keycloak_token(issuer_url=host, token=token)
    else:
        success, data = idp_get_request(url_path=IDP_CONFIG["get_current_login_info"], auth_token=token, host=host)
        if success and data.get("user"):
            if data["tenant"] is None:
                data["tenant"] = {
                    "id": IDP_CONFIG["b2b_id"],
                    "name": IDP_CONFIG["b2b_name"],
                }
            tenant = get_tenant_from_idp_data(data["tenant"])
            return get_user_from_idp_data(data["user"], tenant)
        else:
            raise AuthenticationFailed(_("IDP authentication failed."))
