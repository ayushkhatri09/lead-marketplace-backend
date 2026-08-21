# import code

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import AllowAny
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.tokens import RefreshToken
# from .models import User
# from django.contrib.auth.hashers import check_password

# from .serializers import UserRegisterSerializer,UserLoginSerializer,UserProfileSerializer,LogoutSerializer

# import os

# from django.conf import settings
# from django.shortcuts import redirect

# from google_auth_oauthlib.flow import Flow
# from google.oauth2 import id_token
# from google.auth.transport import requests as google_requests

import secrets
import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from django.shortcuts import redirect
from django.core.cache import cache

from .models import User
from django.contrib.auth.hashers import check_password

from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    LogoutSerializer,
    UserOnboardingSerializer,
)

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests



class UserRegisterAPIView(APIView):
    permission_classes = [AllowAny]


    def post(self, request):

        serializer = UserRegisterSerializer(
            data=request.data
        )


        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "message":"User registered successfully"
                },
                status=status.HTTP_201_CREATED
            )


        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserLoginAPIView(APIView):

    permission_classes = [AllowAny]


    def post(self, request):

        serializer = UserLoginSerializer(
            data=request.data
        )


        if serializer.is_valid():

            phone = serializer.validated_data.get("phone")
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")


            # Find user by phone or email

            try:

                if phone:

                    user = User.objects.get(
                        phone=phone
                    )

                else:

                    user = User.objects.get(
                        email=email
                    )


            except User.DoesNotExist:

                return Response(
                    {
                        "error":"User not found"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )


            # Check password

            if check_password(
                password,
                user.password
            ):


                refresh = RefreshToken.for_user(user)


                return Response(
                    {
                        "message":"Login successful",

                        "refresh":str(refresh),

                        "access":str(
                            refresh.access_token
                        )
                    },
                    status=status.HTTP_200_OK
                )


            return Response(
                {
                    "error":"Invalid password"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )


        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class UserProfileAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]


    def get(self, request):

        user = request.user


        serializer = UserProfileSerializer(
            user
        )


        return Response(
            serializer.data
        )

class UserLogoutAPIView(APIView):

    permission_classes = [IsAuthenticated]


    def post(self, request):

        serializer = LogoutSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )


        try:

            refresh_token = RefreshToken(
                serializer.validated_data["refresh"]
            )

            refresh_token.blacklist()


            return Response(
                {
                    "message": "Logout successfully."
                },
                status=status.HTTP_200_OK
            )


        except Exception:

            return Response(
                {
                    "message": "Invalid refresh token."
                },
                status=status.HTTP_400_BAD_REQUEST
            )    


# ============================================================
# USER GOOGLE LOGIN
# ============================================================

class GoogleLoginAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        print("\n====================================")
        print("USER GOOGLE LOGIN")
        print("====================================")

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

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

        # ----------------------------------------------------
        # Create OAuth Flow
        # ----------------------------------------------------

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
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
        )

        flow.redirect_uri = redirect_uri

        # ----------------------------------------------------
        # Generate PKCE verifier
        # ----------------------------------------------------

        code_verifier = secrets.token_urlsafe(64)

        flow.code_verifier = code_verifier

        # ----------------------------------------------------
        # Generate Google authorization URL
        # ----------------------------------------------------

        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="select_account",
        )

        # ----------------------------------------------------
        # Save OAuth state + PKCE verifier in Django cache
        # ----------------------------------------------------

        oauth_cache_key = f"google_oauth_state:{state}"

        cache.set(
            oauth_cache_key,
            {
                "code_verifier": code_verifier,
            },
            timeout=600,
        )

        print("OAuth State:", state)

        print(
            "OAuth state saved in cache:",
            bool(cache.get(oauth_cache_key))
        )

        print(
            "Verifier saved:",
            bool(code_verifier)
        )

        print("====================================\n")

        return Response(
            {
                "authorization_url": authorization_url
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# USER GOOGLE CALLBACK
# ============================================================

class GoogleCallbackAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        print("\n====================================")
        print("USER GOOGLE CALLBACK")
        print("====================================")

        print(
            "Session ID:",
            request.session.session_key
        )

        print(
            "Session Data:",
            dict(request.session)
        )

        print(
            "Cookies:",
            request.COOKIES
        )

        code = request.GET.get("code")
        state = request.GET.get("state")

        print(
            "Google State:",
            state
        )

        print(
            "Saved State:",
            request.session.get(
                "google_oauth_state"
            )
        )

        print("====================================")

        # ----------------------------------------------------
        # Check authorization code
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Check state
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Get OAuth state data from cache
        # ----------------------------------------------------

        oauth_cache_key = f"google_oauth_state:{state}"

        oauth_data = cache.get(
            oauth_cache_key
        )

        if not oauth_data:
            return Response(
                {
                    "error": (
                        "Google OAuth session expired. "
                        "Please try again."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Get PKCE verifier
        # ----------------------------------------------------

        code_verifier = oauth_data.get(
            "code_verifier"
        )

        if not code_verifier:
            return Response(
                {
                    "error": (
                        "Google OAuth code verifier missing. "
                        "Please try again."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Delete OAuth state immediately
        # Makes state single-use
        # ----------------------------------------------------

        cache.delete(
            oauth_cache_key
        )

        # ----------------------------------------------------
        # Google credentials
        # ----------------------------------------------------

        client_id = os.getenv(
            "GOOGLE_CLIENT_ID"
        )

        client_secret = os.getenv(
            "GOOGLE_CLIENT_SECRET"
        )

        redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI"
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

            # ------------------------------------------------
            # Create OAuth Flow
            # ------------------------------------------------

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
                    "https://www.googleapis.com/auth/userinfo.email",
                    "https://www.googleapis.com/auth/userinfo.profile",
                ],
                state=state,
            )

            flow.redirect_uri = redirect_uri

            # ------------------------------------------------
            # Restore PKCE verifier
            # ------------------------------------------------

            flow.code_verifier = code_verifier

            # ------------------------------------------------
            # Exchange authorization code
            # ------------------------------------------------

            flow.fetch_token(
                code=code
            )

            credentials = flow.credentials

            # ------------------------------------------------
            # Verify Google ID token
            # ------------------------------------------------

            google_id_info = id_token.verify_oauth2_token(
                credentials.id_token,
                google_requests.Request(),
                client_id,
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

            # ------------------------------------------------
            # Validate Google information
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Find user by Google ID
            # ------------------------------------------------

            user = User.objects.filter(
                google_id=google_id
            ).first()

            # ------------------------------------------------
            # Find user by email
            # ------------------------------------------------

            if not user:
                user = User.objects.filter(
                    email=email
                ).first()

            # ------------------------------------------------
            # Create new user
            # ------------------------------------------------

            if not user:

                user = User.objects.create_user(
                    phone=None,
                    email=email,
                    full_name=full_name,
                    google_id=google_id,
                )

            # ------------------------------------------------
            # Existing user
            # ------------------------------------------------

            else:

                update_fields = []

                if not user.google_id:

                    user.google_id = google_id

                    update_fields.append(
                        "google_id"
                    )

                if (
                    not user.full_name
                    and full_name
                ):

                    user.full_name = full_name

                    update_fields.append(
                        "full_name"
                    )

                if update_fields:

                    user.save(
                        update_fields=update_fields
                    )

            # ------------------------------------------------
            # Generate JWT
            # ------------------------------------------------

            refresh = RefreshToken.for_user(
                user
            )

            access_token = str(
                refresh.access_token
            )

            refresh_token = str(
                refresh
            )

            # ------------------------------------------------
            # Create one-time exchange code
            # ------------------------------------------------

            exchange_code = secrets.token_urlsafe(
                32
            )

            cache_key = (
                f"user_google_oauth_code:"
                f"{exchange_code}"
            )

            # ------------------------------------------------
            # Store tokens temporarily
            # ------------------------------------------------

            cache.set(
                cache_key,
                {
                    "access": access_token,
                    "refresh": refresh_token,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "phone": user.phone,
                    },
                },
                timeout=60,
            )

            # ------------------------------------------------
            # Remove old session OAuth data
            # ------------------------------------------------

            # request.session.pop(
            #     "google_oauth_state",
            #     None
            # )

            # request.session.pop(
            #     "google_code_verifier",
            #     None
            # )

            # request.session.save()

            # ------------------------------------------------
            # Redirect to Next.js
            # ------------------------------------------------

            frontend_url = os.getenv(
                "FRONTEND_URL",
                "http://127.0.0.1:3000"
            )

            return redirect(
                f"{frontend_url}"
                f"/user/login/google/callback"
                f"?code={exchange_code}"
            )

        except Exception as e:

            print(
                "\nGOOGLE CALLBACK ERROR:",
                str(e)
            )

            return Response(
                {
                    "error": (
                        "Google authentication failed."
                    ),
                    "details": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================
# USER GOOGLE EXCHANGE
# ============================================================

class UserGoogleExchangeAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        code = request.data.get(
            "code"
        )

        if not code:
            return Response(
                {
                    "error": (
                        "Google exchange code "
                        "is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = (
            f"user_google_oauth_code:{code}"
        )

        auth_data = cache.get(
            cache_key
        )

        if not auth_data:
            return Response(
                {
                    "error": (
                        "Invalid or expired Google "
                        "authentication code."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Single-use code
        # ----------------------------------------------------

        cache.delete(
            cache_key
        )

        return Response(
            {
                "access": auth_data["access"],
                "refresh": auth_data["refresh"],
                "user": auth_data["user"],
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# USER ONBOARDING
# ============================================================

class UserOnboardingAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        user = request.user

        serializer = UserOnboardingSerializer(
            user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "message": (
                        "User onboarding completed "
                        "successfully."
                    ),
                    "user": UserProfileSerializer(
                        user
                    ).data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )