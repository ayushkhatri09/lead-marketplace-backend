from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Service

SERVICE_LIST_CACHE_KEY = "service_list_v1"


@receiver(post_save, sender=Service)
@receiver(post_delete, sender=Service)
def clear_service_list_cache(sender, **kwargs):
    cache.delete(SERVICE_LIST_CACHE_KEY)