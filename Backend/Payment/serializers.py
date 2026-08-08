from rest_framework import serializers

from .models import Payment


class CreateOrderSerializer(serializers.Serializer):

    lead_id = serializers.IntegerField()


class PaymentSerializer(serializers.ModelSerializer):

    provider_name = serializers.CharField(
        source="provider.full_name",
        read_only=True
    )

    customer_name = serializers.CharField(
        source="lead.user.full_name",
        read_only=True
    )

    service_name = serializers.CharField(
        source="lead.service.name",
        read_only=True
    )

    class Meta:
        model = Payment

        fields = [
            "id",
            "provider",
            "provider_name",
            "lead",
            "customer_name",
            "service_name",
            "amount",
            "status",
            "razorpay_order_id",
            "razorpay_payment_id",
            "paid_at",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "provider",
            "provider_name",
            "customer_name",
            "service_name",
            "status",
            "razorpay_order_id",
            "razorpay_payment_id",
            "paid_at",
            "created_at",
        ]