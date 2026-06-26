from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from accounts.models import User


@receiver(pre_save, sender=User)
def deactivate_provider_services(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return
    if old.is_active_provider and not instance.is_active_provider:
        from services.models import Service
        Service.objects.filter(provider=instance).update(status=Service.Status.INACTIVE)
