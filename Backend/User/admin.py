from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ("id", "phone", "email", "full_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_superuser")

    ordering = ("id",)
    search_fields = ("phone", "email", "full_name")

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Personal Info", {"fields": ("full_name", "email", "address", "latitude", "longitude")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone", "email", "full_name", "address", "latitude", "longitude", "password1", "password2", "is_staff", "is_active"),
        }),
    )
