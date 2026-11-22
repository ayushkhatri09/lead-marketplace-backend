# from django.apps import AppConfig


# class ServiceConfig(AppConfig):
#     name = 'Service'

from django.apps import AppConfig


class ServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Service"

    def ready(self):
        from . import signals  # noqa: F401
