from django.db import models

from User.models import User
from Service.models import Service
from Provider.models import Provider

class Lead(models.Model):
    STATUS_CHOICES = (
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("assigned", "Assigned"),
)
    user=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lead'
     )

    service=models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='lead'
     )

    description=models.TextField()

    address=models.TextField()

    latitude=models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    longitude=models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    provider = models.ForeignKey(
    Provider,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="accepted_leads",
)
    payment_status = models.BooleanField(
    default=False
)

    status=models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )

    created_at=models.DateTimeField(
        auto_now_add=True
    )



    def __str__(self):
        return self.description
