from django.utils import timezone

from reminders.services import calculate_reminder_due_date


def sync_document_reminder(document):
    from reminders.models import Reminder

    Reminder.objects.update_or_create(
        source_document=document,
        defaults={
            "reminder_title": f"Document expiry: {document.document_title}",
            "due_date": calculate_reminder_due_date(document.expiry_date),
            "customer": document.customer,
            "notes": document.notes or f"Follow up 10 days before {document.document_title} expires.",
            "is_deleted": False,
            "deleted_at": None,
        },
    )


def deactivate_document_reminder(document):
    from reminders.models import Reminder

    Reminder.objects.filter(source_document=document, is_deleted=False).update(
        is_deleted=True,
        deleted_at=timezone.now(),
    )
