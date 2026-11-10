from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from reminders.services import (
    deactivate_source_reminder,
    deactivate_source_reminders,
    sync_source_reminder,
)

from .models import GovernmentInvoice, GovernmentInvoiceItem


@receiver(post_save, sender=GovernmentInvoiceItem)
def sync_government_invoice_item_reminder(sender, instance, **kwargs):
    invoice = instance.invoice
    if invoice.is_deleted:
        deactivate_source_reminder(instance)
        return
    sync_source_reminder(
        instance,
        reminder_title=f"Govt. invoice {invoice.invoice_number}: {instance.service.name} expiry",
        expiry_date=instance.end_date,
        customer=invoice.customer,
        notes=invoice.notes or f"Follow up 10 days before {instance.service.name} expires.",
    )


@receiver(post_delete, sender=GovernmentInvoiceItem)
def deactivate_deleted_government_invoice_item_reminder(sender, instance, **kwargs):
    deactivate_source_reminder(instance)


@receiver(post_save, sender=GovernmentInvoice)
def deactivate_deleted_government_invoice_reminders(sender, instance, **kwargs):
    if instance.is_deleted:
        deactivate_source_reminders(instance.items.all())
