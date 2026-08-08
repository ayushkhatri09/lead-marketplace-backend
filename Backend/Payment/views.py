from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from Provider.models import Provider
from Lead.models import Lead

from .models import Payment
from Notification.models import Notification
from .serializers import (
    CreateOrderSerializer,
    PaymentSerializer,
)

import razorpay

from .razorpay_client import client

from Provider.authentication import ProviderJWTAuthentication
from Provider.permissions import IsProviderAuthenticated


class CreateOrderAPIView(APIView):

    permission_classes = [IsProviderAuthenticated]

    authentication_classes = [ProviderJWTAuthentication]

    def post(self, request):

        print("PAYMENT REQUEST DATA:", request.data)

        # -------------------------
        # Validate request
        # -------------------------

        serializer = CreateOrderSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            print(
                "PAYMENT SERIALIZER ERROR:",
                serializer.errors
            )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        lead_id = serializer.validated_data["lead_id"]

        # -------------------------
        # Provider
        # -------------------------

        provider = request.user

        if not provider:
            return Response(
                {
                    "message": "Provider authentication required."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # -------------------------
        # Lead
        # -------------------------

        try:

            lead = Lead.objects.get(
                id=lead_id
            )

        except Lead.DoesNotExist:

            return Response(
                {
                    "message": "Lead not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # -------------------------
        # Razorpay Order
        # -------------------------

        try:

            order = client.order.create(
                {
                    "amount": 9900,
                    "currency": "INR",
                    "payment_capture": 1,
                }
            )

        except Exception as error:

            print(
                "RAZORPAY ORDER ERROR:",
                error
            )

            return Response(
                {
                    "message": "Unable to create Razorpay order."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # -------------------------
        # Payment Entry
        # -------------------------

        payment, created = Payment.objects.get_or_create(

            provider=provider,

            lead=lead,

            defaults={
                "amount": Decimal("99.00"),
                "status": "pending",
                "razorpay_order_id": order["id"],
            },
        )

        # Existing payment
        if not created:

            payment.amount = Decimal("99.00")

            payment.status = "pending"

            payment.razorpay_order_id = order["id"]

            payment.save()

        # -------------------------
        # Response
        # -------------------------

        return Response(
            {
                "message": "Order created successfully.",

                "payment": PaymentSerializer(
                    payment
                ).data,

                "order_id": order["id"],

                "amount": payment.amount,

                "key": settings.RAZORPAY_KEY_ID,
            },

            status=status.HTTP_200_OK
        )

# class VerifyPaymentAPIView(APIView):

#     permission_classes = [IsProviderAuthenticated]
#     authentication_classes = [ProviderJWTAuthentication]

#     def post(self, request):

#         print("VERIFY PAYMENT DATA:", request.data)

#         razorpay_order_id = request.data.get(
#             "razorpay_order_id"
#         )

#         razorpay_payment_id = request.data.get(
#             "razorpay_payment_id"
#         )

#         razorpay_signature = request.data.get(
#             "razorpay_signature"
#         )

#         # --------------------------------
#         # Check payment data
#         # --------------------------------

#         if not all([
#             razorpay_order_id,
#             razorpay_payment_id,
#             razorpay_signature,
#         ]):

#             return Response(
#                 {
#                     "message": "Payment verification data is missing."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # --------------------------------
#         # Verify Razorpay Signature
#         # --------------------------------

#         try:

#             client.utility.verify_payment_signature(
#                 {
#                     "razorpay_order_id": razorpay_order_id,
#                     "razorpay_payment_id": razorpay_payment_id,
#                     "razorpay_signature": razorpay_signature,
#                 }
#             )

#         except razorpay.errors.SignatureVerificationError:

#             return Response(
#                 {
#                     "message": "Invalid payment signature."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         except Exception as error:

#             print(
#                 "RAZORPAY VERIFICATION ERROR:",
#                 error
#             )

#             return Response(
#                 {
#                     "message": "Payment verification failed."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # --------------------------------
#         # Provider
#         # --------------------------------

#         provider = request.user

#         # --------------------------------
#         # Payment
#         # --------------------------------

#         try:

#             payment = Payment.objects.select_related(
#                 "lead"
#             ).get(
#                 razorpay_order_id=razorpay_order_id,
#                 provider=provider,
#             )

#         except Payment.DoesNotExist:

#             return Response(
#                 {
#                     "message": "Payment record not found."
#                 },
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         # --------------------------------
#         # Lead
#         # --------------------------------

#         lead = payment.lead

#         # --------------------------------
#         # Prevent duplicate verification
#         # --------------------------------

#         if payment.status == "success":

#             return Response(
#                 {
#                     "message": "Payment already verified.",
#                     "lead_id": lead.id,
#                     "lead_status": lead.status,
#                 },
#                 status=status.HTTP_200_OK
#             )

#         # --------------------------------
#         # Update Payment
#         # --------------------------------

#         payment.status = "success"

#         payment.razorpay_payment_id = (
#             razorpay_payment_id
#         )

#         payment.razorpay_signature = (
#             razorpay_signature
#         )

#         payment.paid_at = timezone.now()

#         payment.save()

#         # --------------------------------
#         # Assign Lead
#         # --------------------------------

#         lead.provider = provider

#         lead.payment_status = True

#         lead.status = "assigned"

#         lead.save(
#             update_fields=[
#                 "provider",
#                 "payment_status",
#                 "status",
#             ]
#         )

#         # --------------------------------
#         # Response
#         # --------------------------------

#         return Response(
#             {
#                 "message": (
#                     "Payment verified and "
#                     "lead assigned successfully."
#                 ),

#                 "lead_id": lead.id,

#                 "provider_id": provider.id,

#                 "payment_status": True,

#                 "lead_status": lead.status,
#             },
#             status=status.HTTP_200_OK
#         )    

from django.db import transaction
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import razorpay

from Provider.authentication import ProviderJWTAuthentication
from Provider.permissions import IsProviderAuthenticated

from Notification.models import Notification

from .models import Payment
from .razorpay_client import client


class VerifyPaymentAPIView(APIView):

    permission_classes = [IsProviderAuthenticated]
    authentication_classes = [ProviderJWTAuthentication]

    def post(self, request):

        print("VERIFY PAYMENT DATA:", request.data)

        razorpay_order_id = request.data.get(
            "razorpay_order_id"
        )

        razorpay_payment_id = request.data.get(
            "razorpay_payment_id"
        )

        razorpay_signature = request.data.get(
            "razorpay_signature"
        )

        # --------------------------------
        # Check payment data
        # --------------------------------

        if not all([
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature,
        ]):

            return Response(
                {
                    "message": "Payment verification data is missing."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # --------------------------------
        # Verify Razorpay Signature
        # --------------------------------

        try:

            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                }
            )

        except razorpay.errors.SignatureVerificationError:

            return Response(
                {
                    "message": "Invalid payment signature."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as error:

            print(
                "RAZORPAY VERIFICATION ERROR:",
                error
            )

            return Response(
                {
                    "message": "Payment verification failed."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # --------------------------------
        # Provider
        # --------------------------------

        provider = request.user

        # --------------------------------
        # Payment
        # --------------------------------

        try:

            payment = Payment.objects.select_related(
                "lead",
                "lead__user",
                "lead__service",
            ).get(
                razorpay_order_id=razorpay_order_id,
                provider=provider,
            )

        except Payment.DoesNotExist:

            return Response(
                {
                    "message": "Payment record not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # --------------------------------
        # Lead
        # --------------------------------

        lead = payment.lead

        # --------------------------------
        # Prevent duplicate verification
        # --------------------------------

        if payment.status == "success":

            return Response(
                {
                    "message": "Payment already verified.",
                    "lead_id": lead.id,
                    "lead_status": lead.status,
                },
                status=status.HTTP_200_OK
            )

        # --------------------------------
        # Payment + Lead + Notification
        # --------------------------------

        try:

            with transaction.atomic():

                # ----------------------------
                # Update Payment
                # ----------------------------

                payment.status = "success"

                payment.razorpay_payment_id = (
                    razorpay_payment_id
                )

                payment.razorpay_signature = (
                    razorpay_signature
                )

                payment.paid_at = timezone.now()

                payment.save()

                # ----------------------------
                # Assign Lead
                # ----------------------------

                lead.provider = provider

                lead.payment_status = True

                lead.status = "assigned"

                lead.save(
                    update_fields=[
                        "provider",
                        "payment_status",
                        "status",
                    ]
                )

                # ----------------------------
                # Create Notification
                # ----------------------------

                Notification.objects.create(

                    user=lead.user,

                    provider=provider,

                    lead=lead,

                    title="Provider Assigned",

                    message=(
                        f"{provider.full_name} has been assigned "
                        f"to your {lead.service.name} service request."
                    ),
                )

        except Exception as error:

            print(
                "PAYMENT FINALIZATION ERROR:",
                error
            )

            return Response(
                {
                    "message": (
                        "Payment was verified, "
                        "but lead assignment failed."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # --------------------------------
        # Response
        # --------------------------------

        return Response(
            {
                "message": (
                    "Payment verified, lead assigned "
                    "and notification created successfully."
                ),

                "lead_id": lead.id,

                "provider_id": provider.id,

                "provider_name": provider.full_name,

                "provider_phone": provider.phone,

                "service_name": lead.service.name,

                "payment_status": True,

                "lead_status": lead.status,
            },
            status=status.HTTP_200_OK
        )