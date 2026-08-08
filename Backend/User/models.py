from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    full_name = models.CharField(
        max_length=150
    )

    phone = models.CharField(
        max_length=15,
        unique=True
    )

    email = models.EmailField(
        unique=True
    )

    address = models.TextField(
        null=True,
        blank=True
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )


    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )


    USERNAME_FIELD = "phone"

    REQUIRED_FIELDS = [
        "email"
    ]


    objects = UserManager()


    def __str__(self):
        return self.phone