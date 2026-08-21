import os
import secrets

from django.shortcuts import redirect

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from django.contrib.auth.hashers import check_password

from .models import Provider
from .authentication import ProviderJWTAuthentication
from .permissions import IsProviderAuthenticated

from .serializers import (
    ProviderRegisterSerializer,
    ProviderLoginSerializer,
    ProviderProfileSerializer,
    NearbyProviderSerializer,
    ProviderOnboardingSerializer,
)

from .utils import haversine

import secrets
from django.shortcuts import redirect
from django.core.cache import cache


class ProviderRegisterAPIView(APIView):

    permission_classes = [
        AllowAny
    ]


    def post(self, request):

        serializer = ProviderRegisterSerializer(
            data=request.data
        )


        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "message": "Provider registered successfully"
                },
                status=status.HTTP_201_CREATED
            )


        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class ProviderOnboardingAPIView(APIView):

    authentication_classes = [ProviderJWTAuthentication]
    permission_classes = [IsProviderAuthenticated]

    def patch(self, request):

        provider = request.user

        serializer = ProviderOnboardingSerializer(
            provider,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {
                "message": "Onboarding completed successfully.",
                "provider": ProviderProfileSerializer(provider).data,
            },
            status=status.HTTP_200_OK,
        )


class ProviderLoginAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ProviderLoginSerializer(data=request.data)

        if serializer.is_valid():

            phone = serializer.validated_data.get("phone")
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

            try:

                if phone:
                    provider = Provider.objects.get(phone=phone)
                else:
                    provider = Provider.objects.get(email=email)

            except Provider.DoesNotExist:

                return Response(
                    {
                        "message": "Provider not found"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            if not check_password(password, provider.password):

                return Response(
                    {
                        "message": "Invalid password"
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Create JWT
            refresh = RefreshToken()

            refresh["provider_id"] = provider.id
            refresh["role"] = "provider"

            access = refresh.access_token

            return Response(
               {
        "message": "Login successful",

        "refresh": str(refresh),
        "access": str(access),

        "provider": {
            "id": provider.id,
            "full_name": provider.full_name,
            "email": provider.email,
            "phone": provider.phone,
            "service": provider.service.name if provider.service else None,
        }
    },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

# class ProviderGoogleLoginAPIView(APIView):

#     permission_classes = [AllowAny]

#     def get(self, request):

#         client_id = os.getenv("GOOGLE_CLIENT_ID")
#         client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
#         redirect_uri = os.getenv(
#     "GOOGLE_PROVIDER_REDIRECT_URI"
# )

#         if not client_id or not client_secret or not redirect_uri:

#             return Response(
#                 {
#                     "error": "Google OAuth credentials are not configured."
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#         try:

#             flow = Flow.from_client_config(
#                 {
#                     "web": {
#                         "client_id": client_id,
#                         "client_secret": client_secret,
#                         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#                         "token_uri": "https://oauth2.googleapis.com/token",
#                     }
#                 },
#                 scopes=[
#                     "openid",
#                     "https://www.googleapis.com/auth/userinfo.email",
#                     "https://www.googleapis.com/auth/userinfo.profile",
#                 ],
#             )

#             flow.redirect_uri = redirect_uri

#             # Generate PKCE verifier
#             code_verifier = secrets.token_urlsafe(64)

#             flow.code_verifier = code_verifier

#             authorization_url, state = flow.authorization_url(
#                 access_type="offline",
#                 include_granted_scopes="true",
#                 prompt="select_account",
#                 code_challenge_method="S256",
#             )

#             # Save OAuth data in Django session
#             request.session["provider_google_oauth_state"] = state

#             request.session["provider_google_code_verifier"] = (
#                 code_verifier
#             )

#             request.session.save()
#             print("\n====================================")
#             print("GOOGLE PROVIDER LOGIN DEBUG")
#             print("====================================")
#             print("Session ID:", request.session.session_key)
#             print("Session data:", dict(request.session))
#             print("Generated state:", state)
#             print("Saved state:", request.session.get(
#                 "provider_google_oauth_state"
#             ))
#             print("Verifier exists:", bool(
#                 request.session.get(
#                     "provider_google_code_verifier"
#                 )
#             ))
#             print("====================================\n")

#             return Response(
#                 {
#                     "authorization_url": authorization_url
#                 },
#                 status=status.HTTP_200_OK
#             )

#         except Exception as e:

#             return Response(
#                 {
#                     "error": "Unable to start Google authentication.",
#                     "details": str(e),
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

class ProviderGoogleLoginAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        print("\n====================================")
        print("PROVIDER GOOGLE LOGIN")
        print("====================================")

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        redirect_uri = os.getenv(
            "GOOGLE_PROVIDER_REDIRECT_URI"
        )

        if not client_id or not client_secret or not redirect_uri:

            return Response(
                {
                    "error": (
                        "Google OAuth credentials "
                        "are not configured."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:

            # --------------------------------
            # Create OAuth Flow
            # --------------------------------

            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": (
                            "https://accounts.google.com/o/oauth2/auth"
                        ),
                        "token_uri": (
                            "https://oauth2.googleapis.com/token"
                        ),
                    }
                },
                scopes=[
                    "openid",
                    (
                        "https://www.googleapis.com/auth/"
                        "userinfo.email"
                    ),
                    (
                        "https://www.googleapis.com/auth/"
                        "userinfo.profile"
                    ),
                ],
            )

            flow.redirect_uri = redirect_uri

            # --------------------------------
            # Generate PKCE verifier
            # --------------------------------

            code_verifier = secrets.token_urlsafe(64)

            flow.code_verifier = code_verifier

            # --------------------------------
            # Generate Google authorization URL
            # --------------------------------

            authorization_url, state = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="select_account",
                code_challenge_method="S256",
            )

            # --------------------------------
            # Save OAuth state + verifier
            # in Django CACHE
            # --------------------------------

            oauth_cache_key = (
                f"provider_google_oauth_state:{state}"
            )

            cache.set(
                oauth_cache_key,
                {
                    "code_verifier": code_verifier,
                },
                timeout=600,  # 10 minutes
            )

            # --------------------------------
            # Debug
            # --------------------------------

            print("Generated State:", state)

            print(
                "OAuth state saved in cache:",
                bool(
                    cache.get(
                        oauth_cache_key
                    )
                )
            )

            print(
                "Verifier saved:",
                bool(code_verifier)
            )

            print(
                "Redirect URI:",
                redirect_uri
            )

            print("====================================\n")

            return Response(
                {
                    "authorization_url": authorization_url
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:

            print(
                "PROVIDER GOOGLE LOGIN ERROR:",
                str(e)
            )

            return Response(
                {
                    "error": (
                        "Unable to start Google "
                        "authentication."
                    ),
                    "details": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )


# class ProviderGoogleCallbackAPIView(APIView):

#     permission_classes = [AllowAny]

#     def get(self, request):
#         print("\n====================================")
#         print("GOOGLE PROVIDER CALLBACK DEBUG")
#         print("====================================")

#         print("Session ID:", request.session.session_key)

#         print("Session data:")
#         print(dict(request.session))

#         print("Cookies:")
#         print(request.COOKIES)

#         print("Google state:")
#         print(request.GET.get("state"))

#         print("Saved OAuth state:")
#         print(
#             request.session.get(
#                 "provider_google_oauth_state"
#             )
#         )

#         print("Saved code verifier:")
#         print(
#             bool(
#                 request.session.get(
#                     "provider_google_code_verifier"
#                 )
#             )
#         )

#         print("====================================\n")    

#         code = request.GET.get("code")
#         state = request.GET.get("state")

#         if not code:

#             return Response(
#                 {
#                     "error": "Google authorization code is missing."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if not state:

#             return Response(
#                 {
#                     "error": "Google OAuth state is missing."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # --------------------------------
#         # Get saved OAuth state
#         # --------------------------------

#         saved_state = request.session.get(
#             "provider_google_oauth_state"
#         )

#         if not saved_state:

#             return Response(
#                 {
#                     "error": (
#                         "Google OAuth session expired. "
#                         "Please try again."
#                     )
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if state != saved_state:

#             return Response(
#                 {
#                     "error": "Invalid Google OAuth state."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # --------------------------------
#         # Get saved PKCE verifier
#         # --------------------------------

#         code_verifier = request.session.get(
#             "provider_google_code_verifier"
#         )

#         if not code_verifier:

#             return Response(
#                 {
#                     "error": (
#                         "Google OAuth code verifier missing. "
#                         "Please try again."
#                     )
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         client_id = os.getenv("GOOGLE_CLIENT_ID")
#         client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
#         redirect_uri = os.getenv(
#     "GOOGLE_PROVIDER_REDIRECT_URI"
# )

#         if not client_id or not client_secret or not redirect_uri:

#             return Response(
#                 {
#                     "error": "Google OAuth credentials are not configured."
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#         try:

#             # --------------------------------
#             # Create OAuth flow
#             # --------------------------------

#             flow = Flow.from_client_config(
#                 {
#                     "web": {
#                         "client_id": client_id,
#                         "client_secret": client_secret,
#                         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#                         "token_uri": "https://oauth2.googleapis.com/token",
#                     }
#                 },
#                 scopes=[
#                     "openid",
#                     "https://www.googleapis.com/auth/userinfo.email",
#                     "https://www.googleapis.com/auth/userinfo.profile",
#                 ],
#                 state=state,
#             )

#             flow.redirect_uri = redirect_uri

#             # IMPORTANT:
#             # Restore PKCE verifier
#             flow.code_verifier = code_verifier

#             # --------------------------------
#             # Exchange code for token
#             # --------------------------------

#             flow.fetch_token(
#                 code=code
#             )

#             credentials = flow.credentials

#             # --------------------------------
#             # Verify Google ID token
#             # --------------------------------

#             google_id_info = id_token.verify_oauth2_token(
#                 credentials.id_token,
#                 google_requests.Request(),
#                 client_id,
#             )

#             google_id = google_id_info.get("sub")
#             email = google_id_info.get("email")
#             full_name = google_id_info.get(
#                 "name",
#                 ""
#             )

#             if not google_id or not email:

#                 return Response(
#                     {
#                         "error": (
#                             "Unable to get Google "
#                             "account information."
#                         )
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # --------------------------------
#             # Find Provider by Google ID
#             # --------------------------------

#             provider = Provider.objects.filter(
#                 google_id=google_id
#             ).first()

#             # --------------------------------
#             # If Google ID not found,
#             # search by email
#             # --------------------------------

#             if not provider:

#                 provider = Provider.objects.filter(
#                     email=email
#                 ).first()

#             # --------------------------------
#             # Create new Provider
#             # --------------------------------

#             if not provider:

#                 provider = Provider.objects.create(
#                     full_name=full_name,
#                     email=email,
#                     google_id=google_id,
#                     phone=None,
#                     password=None,
#                 )

#             else:

#                 update_fields = []

#                 # Attach Google account
#                 if not provider.google_id:

#                     provider.google_id = google_id

#                     update_fields.append(
#                         "google_id"
#                     )

#                 # Update name if empty
#                 if not provider.full_name and full_name:

#                     provider.full_name = full_name

#                     update_fields.append(
#                         "full_name"
#                     )

#                 if update_fields:

#                     provider.save(
#                         update_fields=update_fields
#                     )

#             # --------------------------------
#             # Clear OAuth session
#             # --------------------------------

#             request.session.pop(
#                 "provider_google_oauth_state",
#                 None
#             )

#             request.session.pop(
#                 "provider_google_code_verifier",
#                 None
#             )

#             request.session.save()

#             # --------------------------------
#             # Generate Provider JWT
#             # --------------------------------

#                         # --------------------------------
#             # Generate Provider JWT
#             # --------------------------------

#             refresh = RefreshToken()

#             refresh["provider_id"] = provider.id

#             refresh["provider_email"] = provider.email

#             refresh["role"] = "provider"

#             access = refresh.access_token

#             # --------------------------------
#             # Generate short-lived one-time code
#             # --------------------------------

#             one_time_code = secrets.token_urlsafe(32)

#             cache.set(
#                 f"provider_oauth_code:{one_time_code}",
#                 {
#                     "refresh": str(refresh),
#                     "access": str(access),
#                     "provider": {
#                         "id": provider.id,
#                         "full_name": provider.full_name,
#                         "email": provider.email,
#                         "phone": provider.phone,
#                         "service": (
#                             provider.service.name
#                             if provider.service
#                             else None
#                         ),
#                         "is_active": provider.is_active,
#                         "kyc_status": provider.kyc_status,
#                     },
#                 },
#                 timeout=60,
#             )

#             # --------------------------------
#             # Redirect to Next.js with one-time code
#             # --------------------------------

#             frontend_url = os.getenv(
#                 "FRONTEND_URL",
#                 "http://127.0.0.1:3000"
#             )

#             return redirect(
#                 f"{frontend_url}/provider/google/callback"
#                 f"?code={one_time_code}"
#             )

#         except Exception as e:

#             return Response(
#                 {
#                     "error": (
#                         "Google provider authentication failed."
#                     ),
#                     "details": str(e),
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

class ProviderGoogleCallbackAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        print("\n====================================")
        print("PROVIDER GOOGLE CALLBACK")
        print("====================================")

        code = request.GET.get("code")
        state = request.GET.get("state")

        print("Google State:", state)
        print("Code received:", bool(code))

        # --------------------------------
        # Check authorization code
        # --------------------------------

        if not code:

            return Response(
                {
                    "error": (
                        "Google authorization "
                        "code is missing."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # --------------------------------
        # Check state
        # --------------------------------

        if not state:

            return Response(
                {
                    "error": (
                        "Google OAuth state "
                        "is missing."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # --------------------------------
        # Get OAuth data from CACHE
        # --------------------------------

        oauth_cache_key = (
            f"provider_google_oauth_state:{state}"
        )

        oauth_data = cache.get(
            oauth_cache_key
        )

        print(
            "OAuth data found in cache:",
            bool(oauth_data)
        )

        if not oauth_data:

            return Response(
                {
                    "error": (
                        "Provider Google OAuth "
                        "session expired. "
                        "Please try again."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # --------------------------------
        # Get PKCE verifier
        # --------------------------------

        code_verifier = oauth_data.get(
            "code_verifier"
        )

        if not code_verifier:

            return Response(
                {
                    "error": (
                        "Google OAuth code verifier "
                        "missing. Please try again."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # --------------------------------
        # Google credentials
        # --------------------------------

        client_id = os.getenv(
            "GOOGLE_CLIENT_ID"
        )

        client_secret = os.getenv(
            "GOOGLE_CLIENT_SECRET"
        )

        redirect_uri = os.getenv(
            "GOOGLE_PROVIDER_REDIRECT_URI"
        )

        if (
            not client_id
            or not client_secret
            or not redirect_uri
        ):

            return Response(
                {
                    "error": (
                        "Google OAuth credentials "
                        "are not configured."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:

            # --------------------------------
            # Create OAuth Flow
            # --------------------------------

            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": (
                            "https://accounts.google.com/o/oauth2/auth"
                        ),
                        "token_uri": (
                            "https://oauth2.googleapis.com/token"
                        ),
                    }
                },
                scopes=[
                    "openid",
                    (
                        "https://www.googleapis.com/auth/"
                        "userinfo.email"
                    ),
                    (
                        "https://www.googleapis.com/auth/"
                        "userinfo.profile"
                    ),
                ],
                state=state,
            )

            flow.redirect_uri = redirect_uri

            # --------------------------------
            # Restore PKCE verifier
            # --------------------------------

            flow.code_verifier = code_verifier

            # --------------------------------
            # Exchange Google authorization code
            # --------------------------------

            flow.fetch_token(
                code=code
            )

            # --------------------------------
            # OAuth state is now consumed
            # --------------------------------

            cache.delete(
                oauth_cache_key
            )

            credentials = flow.credentials

            # --------------------------------
            # Verify Google ID token
            # --------------------------------

            google_id_info = (
                id_token.verify_oauth2_token(
                    credentials.id_token,
                    google_requests.Request(),
                    client_id,
                )
            )

            google_id = google_id_info.get(
                "sub"
            )

            email = google_id_info.get(
                "email"
            )

            full_name = google_id_info.get(
                "name",
                ""
            )

            # --------------------------------
            # Validate Google information
            # --------------------------------

            if not google_id or not email:

                return Response(
                    {
                        "error": (
                            "Unable to get Google "
                            "account information."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # --------------------------------
            # Find Provider by Google ID
            # --------------------------------

            provider = Provider.objects.filter(
                google_id=google_id
            ).first()

            # --------------------------------
            # Find Provider by email
            # --------------------------------

            if not provider:

                provider = Provider.objects.filter(
                    email=email
                ).first()

            # --------------------------------
            # Create Provider
            # --------------------------------

            if not provider:

                provider = Provider.objects.create(
                    full_name=full_name,
                    email=email,
                    google_id=google_id,
                    phone=None,
                    password=None,
                )

            # --------------------------------
            # Existing Provider
            # --------------------------------

            else:

                update_fields = []

                if not provider.google_id:

                    provider.google_id = google_id

                    update_fields.append(
                        "google_id"
                    )

                if (
                    not provider.full_name
                    and full_name
                ):

                    provider.full_name = full_name

                    update_fields.append(
                        "full_name"
                    )

                if update_fields:

                    provider.save(
                        update_fields=update_fields
                    )

            # --------------------------------
            # Generate Provider JWT
            # --------------------------------

            refresh = RefreshToken()

            refresh["provider_id"] = provider.id

            refresh["provider_email"] = (
                provider.email
            )

            refresh["role"] = "provider"

            access = refresh.access_token

            # --------------------------------
            # Generate one-time exchange code
            # --------------------------------

            one_time_code = (
                secrets.token_urlsafe(32)
            )

            cache.set(
                f"provider_oauth_code:{one_time_code}",
                {
                    "refresh": str(refresh),
                    "access": str(access),

                    "provider": {
                        "id": provider.id,
                        "full_name": provider.full_name,
                        "email": provider.email,
                        "phone": provider.phone,

                        "service": (
                            provider.service.name
                            if provider.service
                            else None
                        ),

                        "is_active": (
                            provider.is_active
                        ),

                        "kyc_status": (
                            provider.kyc_status
                        ),
                    },
                },
                timeout=60,
            )

            # --------------------------------
            # Redirect to Next.js
            # --------------------------------

            frontend_url = os.getenv(
                "FRONTEND_URL",
                "http://127.0.0.1:3000"
            )

            return redirect(
                f"{frontend_url}"
                f"/provider/google/callback"
                f"?code={one_time_code}"
            )

        except Exception as e:

            print(
                "\nPROVIDER GOOGLE CALLBACK ERROR:",
                str(e)
            )

            return Response(
                {
                    "error": (
                        "Google provider "
                        "authentication failed."
                    ),
                    "details": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class ProviderGoogleExchangeAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        code = request.data.get("code")

        if not code:
            return Response(
                {"error": "Code is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f"provider_oauth_code:{code}"

        data = cache.get(cache_key)

        if not data:
            return Response(
                {"error": "Invalid or expired code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # one-time use — turant delete
        cache.delete(cache_key)

        return Response(data, status=status.HTTP_200_OK)                  


class ProviderProfileAPIView(APIView):

    authentication_classes = [ProviderJWTAuthentication]
    permission_classes = [IsProviderAuthenticated]

    def get(self, request):

        provider = request.user

        serializer = ProviderProfileSerializer(provider)

        return Response(
            {
                "message": "Provider profile fetched successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

from rest_framework_simplejwt.views import TokenRefreshView

class ProviderTokenRefreshAPIView(TokenRefreshView):
    pass   


# class NearbyProviderAPIView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):

#         lat = request.GET.get("lat")
#         lng = request.GET.get("lng")

#         if not lat or not lng:
#             return Response(
#                 {
#                     "message": "lat and lng are required."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )


#         # All providers having location

#         providers = Provider.objects.filter(
#             latitude__isnull=False,
#             longitude__isnull=False
#         )


#         MAX_DISTANCE = 10  # KM

#         provider_list = []


#         for provider in providers:

#             distance = haversine(
#                 lat,
#                 lng,
#                 provider.latitude,
#                 provider.longitude
#             )


#             if distance <= MAX_DISTANCE:

#                 serializer = NearbyProviderSerializer(
#                     provider,
#                     context={
#                         "request": request
#                     }
#                 )


#                 data = serializer.data

#                 data["distance"] = round(
#                     distance,
#                     2
#                 )


#                 provider_list.append(data)



#         provider_list = sorted(
#             provider_list,
#             key=lambda x: x["distance"]
#         )


#         return Response(
#             {
#                 "message": "Nearby providers fetched successfully.",
#                 "count": len(provider_list),
#                 "data": provider_list,
#             },
#             status=status.HTTP_200_OK
#         )


class NearbyProviderAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        lat = request.GET.get("lat")
        lng = request.GET.get("lng")

        if not lat or not lng:
            return Response(
                {
                    "message": "lat and lng are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Only ACTIVE providers with location
        providers = Provider.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            is_active=True
        )

        MAX_DISTANCE = 10  # KM

        provider_list = []

        for provider in providers:

            distance = haversine(
                lat,
                lng,
                provider.latitude,
                provider.longitude
            )

            if distance <= MAX_DISTANCE:

                serializer = NearbyProviderSerializer(
                    provider,
                    context={
                        "request": request
                    }
                )

                data = serializer.data

                data["distance"] = round(
                    distance,
                    2
                )

                provider_list.append(data)

        provider_list = sorted(
            provider_list,
            key=lambda x: x["distance"]
        )

        return Response(
            {
                "message": "Nearby active providers fetched successfully.",
                "count": len(provider_list),
                "data": provider_list,
            },
            status=status.HTTP_200_OK
        )


class ToggleProviderActiveAPIView(APIView):

    authentication_classes = [
        ProviderJWTAuthentication
    ]

    permission_classes = [
        IsProviderAuthenticated
    ]

    def post(self, request):

        provider = request.user

        # Active <-> Inactive
        provider.is_active = not provider.is_active

        provider.save(
            update_fields=["is_active"]
        )

        return Response(
            {
                "message": (
                    "Provider is now active."
                    if provider.is_active
                    else "Provider is now inactive."
                ),
                "is_active": provider.is_active,
            },
            status=status.HTTP_200_OK
        )
    