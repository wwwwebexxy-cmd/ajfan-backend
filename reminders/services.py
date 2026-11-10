from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .models import Reminder


def calculate_reminder_due_date(expiry_date):
    return max(expiry_date - timedelta(days=10), timezone.localdate())


def sync_source_reminder(source, *, reminder_title, expiry_date, customer, notes):
    content_type = ContentType.objects.get_for_model(source, for_concrete_model=False)
    return Reminder.objects.update_or_create(
        source_content_type=content_type,
        source_object_id=source.pk,
        defaults={
            "reminder_title": reminder_title,
            "due_date": calculate_reminder_due_date(expiry_date),
            "customer": customer,
            "notes": notes,
            "is_deleted": False,
            "deleted_at": None,
        },
    )


def deactivate_source_reminder(source):
    content_type = ContentType.objects.get_for_model(source, for_concrete_model=False)
    Reminder.objects.filter(
        source_content_type=content_type,
        source_object_id=source.pk,
        is_deleted=False,
    ).update(
        is_deleted=True,
        deleted_at=timezone.now(),
    )


def deactivate_source_reminders(sources):
    sources = list(sources)
    if not sources:
        return
    content_type = ContentType.objects.get_for_model(sources[0], for_concrete_model=False)
    Reminder.objects.filter(
        source_content_type=content_type,
        source_object_id__in=[source.pk for source in sources],
        is_deleted=False,
    ).update(
        is_deleted=True,
        deleted_at=timezone.now(),
    )
