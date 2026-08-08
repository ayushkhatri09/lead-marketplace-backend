from django.urls import path

from .views import MarkNotificationReadAPIView, NotificationListAPIView


urlpatterns = [
    path(
        "",
        NotificationListAPIView.as_view(),
        name="notification-list",
    ),
    path(
        "<int:pk>/read/",
        MarkNotificationReadAPIView.as_view()
    ),

]