# from rest_framework import serializers
# from django.contrib.auth.hashers import make_password
# from Service.models import Service


# from .models import Provider

# class ProviderRegisterSerializer(serializers.ModelSerializer):

#     password = serializers.CharField(
#         write_only=True
#     )

#     service = serializers.PrimaryKeyRelatedField(
#         queryset=Service.objects.filter(is_active=True)
#     )


#     class Meta:

#         model = Provider

#         fields = [
#             "full_name",
#             "phone",
#             "email",
#             "password",

#             "service",

#             # "profile_image",

#             # "aadhaar_front",
#             # "aadhaar_back",
#             # "pan_card",

#             "address",
#             "latitude",
#             "longitude",
#         ]

#         extra_kwargs = {

#             "profile_image": {
#                 "required": False
#             },

#             "aadhaar_front": {
#                 "required": False
#             },

#             "aadhaar_back": {
#                 "required": False
#             },

#             "pan_card": {
#                 "required": False
#             }

#         }


#     def create(self, validated_data):

#         password = validated_data.pop(
#             "password"
#         )


#         provider = Provider.objects.create(
#             password=make_password(password),
#             **validated_data
#         )


#         return provider

# class ProviderLoginSerializer(serializers.Serializer):

#     phone = serializers.CharField(
#         required=False
#     )

#     email = serializers.EmailField(
#         required=False
#     )

#     password = serializers.CharField(
#         write_only=True
#     )


#     def validate(self, data):

#         if not data.get("phone") and not data.get("email"):
#             raise serializers.ValidationError(
#                 "Phone or Email is required."
#             )

#         return data


# from rest_framework import serializers
# from .models import Provider


# class ProviderProfileSerializer(serializers.ModelSerializer):
#     service = serializers.CharField(
#         source="service.name",
#         read_only=True
#     )

#     class Meta:

#         model = Provider

#         fields = [
#             "id",
#             "full_name",
#             "phone",
#             "email",
#             "service",
#             "profile_image",
#             "aadhaar_front",
#             "aadhaar_back",
#             "pan_card",
#             "kyc_status",
#             "address",
#             "latitude",
#             "longitude",
            
#             "created_at",
#         ]

#         read_only_fields = fields    

# class NearbyProviderSerializer(serializers.ModelSerializer):

#     service_name = serializers.CharField(
#         source="service.name",
#         read_only=True
#     )

#     service = serializers.IntegerField(
#     source="service.id",
#     read_only=True
# )

#     profile_image = serializers.SerializerMethodField()

#     class Meta:
#         model = Provider

#         fields = [
#             "id",
#             "full_name",
#             "service",
#             "service_name",
#             "rating",
#             "profile_image",
#             "latitude",
#             "longitude",
#         ]

#     def get_profile_image(self, obj):
#         request = self.context.get("request")

#         if obj.profile_image:
#             return request.build_absolute_uri(obj.profile_image.url)

#         return None

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from Service.models import Service

from .models import Provider


# =========================================================
# PROVIDER REGISTER
# =========================================================

class ProviderRegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
    )

    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(
            is_active=True
        )
    )

    class Meta:

        model = Provider

        fields = [
            "full_name",
            "phone",
            "email",
            "password",
            "service",
            "address",
            "latitude",
            "longitude",
        ]

    def create(self, validated_data):

        password = validated_data.pop(
            "password"
        )

        provider = Provider.objects.create(
            password=make_password(password),
            **validated_data
        )

        return provider


# =========================================================
# PROVIDER LOGIN
# =========================================================

class ProviderLoginSerializer(serializers.Serializer):

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

        if (
            not data.get("phone")
            and not data.get("email")
        ):
            raise serializers.ValidationError(
                "Phone or Email is required."
            )

        return data


# =========================================================
# PROVIDER PROFILE
# =========================================================

class ProviderProfileSerializer(
    serializers.ModelSerializer
):

    service = serializers.CharField(
        source="service.name",
        read_only=True
    )

    class Meta:

        model = Provider

        fields = [
            "id",
            "full_name",
            "phone",
            "email",

            "service",

            "profile_image",

            "aadhaar_front",
            "aadhaar_back",
            "pan_card",

            "kyc_status",

            "address",
            "latitude",
            "longitude",

            "is_active",

            "rating",
            "completed_jobs",

            "created_at",
        ]

        read_only_fields = fields


# =========================================================
# NEARBY PROVIDER
# =========================================================

class NearbyProviderSerializer(
    serializers.ModelSerializer
):

    service_name = serializers.CharField(
        source="service.name",
        read_only=True
    )

    service = serializers.IntegerField(
        source="service.id",
        read_only=True
    )

    profile_image = serializers.SerializerMethodField()

    class Meta:

        model = Provider

        fields = [
            "id",
            "full_name",

            "service",
            "service_name",

            "rating",

            "profile_image",

            "latitude",
            "longitude",

            "is_active",
        ]

        read_only_fields = fields

    def get_profile_image(self, obj):

        request = self.context.get(
            "request"
        )

        if obj.profile_image:

            return request.build_absolute_uri(
                obj.profile_image.url
            )

        return None