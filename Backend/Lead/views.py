from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.db import transaction

from Provider.authentication import ProviderJWTAuthentication

from .models import Lead
from .serializers import LeadCreateSerializer,MyLeadSerializer, ProviderHistorySerializer, ProviderLeadListSerializer
from Provider .models import Provider
from Provider.permissions import IsProviderAuthenticated


class LeadCreateAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):

        serializer=LeadCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response(
                {
                    "message":"lead create succesfully",
                    "data":serializer.data
                },
                status=status.HTTP_201_CREATED

            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST


        )

class MyLeadAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        leads = Lead.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = MyLeadSerializer(
            leads,
            many=True
        )

        return Response(
            {
                "message": "My leads fetched successfully.",
                "count": leads.count(),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

class ProviderLeadListAPIView(APIView):
    permission_classes=[IsProviderAuthenticated]
    authentication_classes = [ProviderJWTAuthentication]

    def get(self,request):

        provider=request.user

        leads=Lead.objects.filter(
            service=provider.service,
            status='pending'
        ).order_by('created_at')

        serializer=ProviderLeadListSerializer(
            leads,
            many=True
        )
        return Response(
            {
                'message':"Available leads fetched successfully.",
                "count": leads.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )

class AcceptLeadAPIView(APIView):

    authentication_classes = [ProviderJWTAuthentication]
    permission_classes = [IsProviderAuthenticated]

    def post(self, request, lead_id):
        return Response(
            {
                "message": "Complete payment to accept this lead."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class PurchaseLeadAPIView(APIView):
    """Completes the lead purchase and reveals customer contact details."""

    authentication_classes = [ProviderJWTAuthentication]
    permission_classes = [IsProviderAuthenticated]

    def post(self, request, lead_id):
        provider = request.user

        with transaction.atomic():
            try:
                lead = Lead.objects.select_for_update().get(
                    id=lead_id,
                    status="pending"
                )
            except Lead.DoesNotExist:
                return Response(
                    {"message": "This lead is no longer available."},
                    status=status.HTTP_404_NOT_FOUND
                )

            if lead.service != provider.service:
                return Response(
                    {"message": "You cannot purchase this lead."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Payment gateway integration can replace this confirmed-payment step.
            lead.provider = provider
            lead.status = "accepted"
            lead.payment_status = True
            lead.save(update_fields=["provider", "status", "payment_status"])

        return Response(
            {
                "message": "Payment successful. Customer contact unlocked.",
                "lead_id": lead.id,
            },
            status=status.HTTP_200_OK
        )

class ProviderHistoryAPIView(APIView):

    authentication_classes = [ProviderJWTAuthentication]
    permission_classes = [IsProviderAuthenticated]

    def get(self, request):

        provider = request.user

        leads = Lead.objects.filter(
            provider=provider,
            status="assigned",
            payment_status=True,
        ).order_by("-created_at")


        serializer = ProviderHistorySerializer(
            leads,
            many=True
        )

        return Response(
            {
                "message": "Provider history fetched successfully.",
                "count": leads.count(),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )          
