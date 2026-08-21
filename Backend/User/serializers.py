from rest_framework import serializers
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
    )


    class Meta:

        model = User

        fields = [
            "full_name",
            "phone",
            "email",
            "password",
            "address",
            "latitude",
            "longitude",
        ]


    def create(self, validated_data):

        user = User.objects.create_user(
            **validated_data
        )

        return user





class UserLoginSerializer(serializers.Serializer):

    phone = serializers.CharField(
        required=False
    )

    email = serializers.EmailField(
        required=False
    )

    password = serializers.CharField(
        write_only=True
    )


    def validate(self, data):

        if not data.get("phone") and not data.get("email"):
            raise serializers.ValidationError(
                "Phone or Email is required"
            )

        return data 



class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:

        model = User

        fields = [
            "id",
            "full_name",
            "phone",
            "email",
            "address",
            "latitude",
            "longitude",
        ] 

class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField() 



class UserOnboardingSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            "phone",
            "address",
            "latitude",
            "longitude",
        ]

        extra_kwargs = {
            "phone": {
                "required": True
            },
            "address": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "latitude": {
                "required": False,
                "allow_null": True,
            },
            "longitude": {
                "required": False,
                "allow_null": True,
            },
        }              






      

    