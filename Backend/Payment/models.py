from django.db import models

from Lead.models import Lead
from Provider.models import Provider


class Payment(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    )

    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=99.00
    )

    razorpay_order_id = models.CharField(
        max_length=255,
        unique=True
    )

    razorpay_payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    razorpay_signature = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["provider", "lead"],
                name="unique_provider_lead_payment"
            )
        ]

    def __str__(self):
        return f"{self.provider.full_name} - Lead #{self.lead.id} - {self.status}"