from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from reminders.services import (
    deactivate_source_reminder,
    deactivate_source_reminders,
    sync_source_reminder,
)

from .models import Quotation, QuotationItem


@receiver(post_save, sender=QuotationItem)
def sync_quotation_item_reminder(sender, instance, **kwargs):
    quotation = instance.quotation
    if quotation.is_deleted:
        deactivate_source_reminder(instance)
        return
    sync_source_reminder(
        instance,
        reminder_title=f"Quotation {quotation.quotation_number}: {instance.service.name} expiry",
        expiry_date=instance.end_date,
        customer=quotation.customer,
        notes=quotation.notes or f"Follow up 10 days before {instance.service.name} expires.",
    )


@receiver(post_delete, sender=QuotationItem)
def deactivate_deleted_quotation_item_reminder(sender, instance, **kwargs):
    deactivate_source_reminder(instance)


@receiver(post_save, sender=Quotation)
def deactivate_deleted_quotation_reminders(sender, instance, **kwargs):
    if instance.is_deleted:
        deactivate_source_reminders(instance.items.all())
