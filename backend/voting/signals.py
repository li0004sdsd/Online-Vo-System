from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Poll, UserActivity
from .moderation import auto_moderate_poll
import threading


@receiver(post_save, sender=User)
def create_user_activity(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.get_or_create(user=instance)


@receiver(post_save, sender=Poll)
def trigger_moderation(sender, instance, created, **kwargs):
    if created and instance.status == Poll.STATUS_PENDING:
        thread = threading.Thread(target=auto_moderate_poll, args=(instance,))
        thread.daemon = True
        thread.start()


def update_user_activity(user):
    if not user or not user.is_authenticated:
        return

    activity, created = UserActivity.objects.get_or_create(user=user)
    activity.last_active = timezone.now()
    activity.save(update_fields=['last_active'])
