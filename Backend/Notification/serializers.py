from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    provider_name = serializers.CharField(
        source="provider.full_name",
        read_only=True
    )

    provider_phone = serializers.CharField(
        source="provider.phone",
        read_only=True
    )

    service_name = serializers.CharField(
        source="lead.service.name",
        read_only=True
    )

    class Meta:
        model = Notification

        fields = [
            "id",
            "title",
            "message",
            "provider_name",
            "provider_phone",
            "service_name",
            "lead",
            "is_read",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "provider_name",
            "provider_phone",
            "service_name",
            "created_at",
        ]