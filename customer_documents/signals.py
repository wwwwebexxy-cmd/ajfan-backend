from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomerDocument
from .services import deactivate_document_reminder, sync_document_reminder


@receiver(post_save, sender=CustomerDocument)
def sync_customer_document_reminder(sender, instance, **kwargs):
    if instance.is_deleted:
        deactivate_document_reminder(instance)
    else:
        sync_document_reminder(instance)
