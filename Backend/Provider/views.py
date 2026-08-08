from urllib import request

from django.core.serializers import python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import AccessToken
from .models import Provider
from .authentication import ProviderJWTAuthentication
from .permissions import IsProviderAuthenticated

from .serializers import ProviderRegisterSerializer, ProviderLoginSerializer,ProviderProfileSerializer
from .serializers import NearbyProviderSerializer
from .utils import haversine
from rest_framework.permissions import AllowAny



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
    