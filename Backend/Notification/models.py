from django.db import models

from User.models import User
from Lead.models import Lead
from Provider.models import Provider


class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )

    provider = models.ForeignKey(
        Provider,
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )

    title = models.CharField(
        max_length=255
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.full_name} - {self.title}"