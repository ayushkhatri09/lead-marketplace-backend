from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "provider",
        "service",
        "status",
        "payment_status",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "service",
    )

    search_fields = (
        "user__full_name",
        "provider__full_name",
        "description",
        "address",
    )

    ordering = (
        "-created_at",
    )