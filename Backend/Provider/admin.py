from django.contrib import admin
from .models import Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone",
        "email",
        "service",
        "kyc_status",
        "created_at",
    )
    search_fields = (
        "full_name",
        "phone",
        "email",
        "service",
    )
    list_filter = (
        "kyc_status",
        "service",
        "created_at",
    )
    readonly_fields = ("created_at",)
    list_editable = ("kyc_status",)
