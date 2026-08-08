from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        notifications = Notification.objects.filter(
            user=request.user
        ).select_related(
            "provider",
            "lead",
            "lead__service"
        ).order_by("-created_at")

        serializer = NotificationSerializer(
            notifications,
            many=True
        )

        return Response(
            {
                "message": "Notifications fetched successfully.",
                "count": notifications.count(),
                "data": serializer.data,
            }
        )

class MarkNotificationReadAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:
            notification = Notification.objects.get(
                id=pk,
                user=request.user
            )

        except Notification.DoesNotExist:

            return Response(
                {
                    "message": "Notification not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )


        notification.is_read = True
        notification.save()


        return Response(
            {
                "message": "Notification marked as read."
            },
            status=status.HTTP_200_OK
        )    