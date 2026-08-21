# from django.db import models


# class Provider(models.Model):

#     full_name = models.CharField(
#         max_length=150
#     )

#     phone = models.CharField(
#         max_length=15,
#         unique=True
#     )

#     email = models.EmailField(
#         unique=True
#     )

#     password = models.CharField(
#         max_length=255
#     )


#     service = models.ForeignKey(
#     "Service.Service",
#     on_delete=models.CASCADE,
#     related_name="providers",
#     null=True,
#     blank=True,
# )


#     # Profile Image
#     profile_image = models.ImageField(
#         upload_to="provider/profile/",
#         null=True,
#         blank=True
#     )


#     # KYC Documents

#     aadhaar_front = models.ImageField(
#         upload_to="provider/kyc/aadhaar/",
#         null=True,
#         blank=True
#     )


#     aadhaar_back = models.ImageField(
#         upload_to="provider/kyc/aadhaar/",
#         null=True,
#         blank=True
#     )


#     pan_card = models.ImageField(
#         upload_to="provider/kyc/pan/",
#         null=True,
#         blank=True
#     )


#     kyc_status = models.CharField(
#         max_length=20,
#         choices=(
#             ("pending","Pending"),
#             ("verified","Verified"),
#             ("rejected","Rejected"),
#         ),
#         default="pending"
#     )

#     is_active = models.BooleanField(
#     default=False
#    )


#     address = models.TextField(
#         null=True,
#         blank=True
#     )


#     latitude = models.DecimalField(
#         max_digits=9,
#         decimal_places=6,
#         null=True,
#         blank=True
#     )


#     longitude = models.DecimalField(
#         max_digits=9,
#         decimal_places=6,
#         null=True,
#         blank=True
#     )


#     created_at = models.DateTimeField(
#         auto_now_add=True
#     )

#     rating = models.DecimalField(
#     max_digits=2,
#     decimal_places=1,
#     default=5.0
# )

#     completed_jobs = models.PositiveIntegerField(
#     default=0
# )


#     def __str__(self):
#         return self.full_name

#     @property
#     def is_authenticated(self):
#         return True

from django.db import models


class Provider(models.Model):

    full_name = models.CharField(
        max_length=150
    )

    phone = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True
    )

    email = models.EmailField(
        unique=True
    )

    google_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    password = models.CharField(
    max_length=255,
    null=True,
    blank=True
)

    service = models.ForeignKey(
        "Service.Service",
        on_delete=models.CASCADE,
        related_name="providers",
        null=True,
        blank=True,
    )

    # Profile Image
    profile_image = models.ImageField(
        upload_to="provider/profile/",
        null=True,
        blank=True
    )

    # KYC Documents
    aadhaar_front = models.ImageField(
        upload_to="provider/kyc/aadhaar/",
        null=True,
        blank=True
    )

    aadhaar_back = models.ImageField(
        upload_to="provider/kyc/aadhaar/",
        null=True,
        blank=True
    )

    pan_card = models.ImageField(
        upload_to="provider/kyc/pan/",
        null=True,
        blank=True
    )

    kyc_status = models.CharField(
        max_length=20,
        choices=(
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ),
        default="pending"
    )

    is_active = models.BooleanField(
        default=False
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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=5.0
    )

    completed_jobs = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return self.full_name

    @property
    def is_authenticated(self):
        return True
