from rest_framework import serializers

from .models import Lead

class  LeadCreateSerializer(serializers.ModelSerializer):

    class Meta:

        model=Lead

        fields=[
            'service',
            'description',
            'address',
            'latitude',
            'longitude',
        ]

class MyLeadSerializer(serializers.ModelSerializer):

    service_name=serializers.CharField(
        source='service.name',
        read_only=True

    )

    provider_name = serializers.CharField(
    source="provider.full_name",
    read_only=True
    )

    provider_phone = serializers.CharField(
    source="provider.phone",
    read_only=True
   )

    service_id = serializers.IntegerField(
    source="service.id",
    read_only=True
)

    class Meta:
        model=Lead

        fields=[
            'id',
            'service_name',
            'service_id',
            'description',
            'address',
            "latitude",
            "longitude",
            "status",
            "payment_status",
            "created_at",
            "provider_name",
            "provider_phone",
        ] 

from rest_framework import serializers
from .models import Lead


class ProviderLeadListSerializer(serializers.ModelSerializer):

    service_name = serializers.CharField(
        source="service.name",
        read_only=True
    )

    user_name = serializers.CharField(
    source="user.full_name",
    read_only=True
)

    class Meta:

        model = Lead

        fields = [
            "id",
            "user_name",
            "service_name",
            "description",
            "address",
            "latitude",
            "longitude",
            "created_at",
        ] 

class ProviderHistorySerializer(serializers.ModelSerializer):

    service_name = serializers.CharField(
        source="service.name",
        read_only=True
    )

    user_name = serializers.CharField(
        source="user.full_name",
        read_only=True
    )

    user_phone = serializers.CharField(
        source="user.phone",
        read_only=True
    )

    class Meta:
        model = Lead

        fields = [
            "id",
            "service_name",
            "user_name",
            "user_phone",
            "description",
            "address",
            "status",
            "created_at",
        ]                   

   
