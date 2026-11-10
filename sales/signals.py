from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from reminders.services import (
    deactivate_source_reminder,
    deactivate_source_reminders,
    sync_source_reminder,
)

from .models import SalesInvoice, SalesInvoiceItem


@receiver(post_save, sender=SalesInvoiceItem)
def sync_sales_invoice_item_reminder(sender, instance, **kwargs):
    invoice = instance.invoice
    if invoice.is_deleted:
        deactivate_source_reminder(instance)
        return
    sync_source_reminder(
        instance,
        reminder_title=f"Sales invoice {invoice.invoice_number}: {instance.service.name} expiry",
        expiry_date=instance.expiry_date,
        customer=invoice.customer,
        notes=invoice.notes or f"Follow up 10 days before {instance.service.name} expires.",
    )


@receiver(post_delete, sender=SalesInvoiceItem)
def deactivate_deleted_sales_invoice_item_reminder(sender, instance, **kwargs):
    deactivate_source_reminder(instance)


@receiver(post_save, sender=SalesInvoice)
def deactivate_deleted_sales_invoice_reminders(sender, instance, **kwargs):
    if instance.is_deleted:
        deactivate_source_reminders(instance.items.all())
