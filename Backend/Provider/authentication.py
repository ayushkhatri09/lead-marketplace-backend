from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed

from .models import Provider


class ProviderJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        try:

            token = auth_header.split(" ")[1]

            access_token = AccessToken(token)

            provider_id = access_token.get("provider_id")

            if not provider_id:
                raise AuthenticationFailed("Invalid provider token.")

            provider = Provider.objects.get(id=provider_id)

            return (provider, None)

        except Provider.DoesNotExist:
            raise AuthenticationFailed("Provider not found.")

        except Exception:
            raise AuthenticationFailed("Invalid or expired token.")