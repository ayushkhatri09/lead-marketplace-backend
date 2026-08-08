from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.contrib.auth.hashers import check_password

from .serializers import UserRegisterSerializer,UserLoginSerializer,UserProfileSerializer,LogoutSerializer



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