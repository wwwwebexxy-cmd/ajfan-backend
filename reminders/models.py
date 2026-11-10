from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from customers.models import Customer


class Reminder(models.Model):
    reminder_title = models.CharField(max_length=180)
    due_date = models.DateField()
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="reminders",
    )
    source_document = models.OneToOneField(
        "customer_documents.CustomerDocument",
        on_delete=models.CASCADE,
        related_name="reminder",
        null=True,
        blank=True,
    )
    source_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reminder_sources",
    )
    source_object_id = models.PositiveBigIntegerField(null=True, blank=True)
    source_object = GenericForeignKey("source_content_type", "source_object_id")
    notes = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("due_date", "reminder_title", "id")
        constraints = (
            models.UniqueConstraint(
                fields=("source_content_type", "source_object_id"),
                name="unique_reminder_generic_source",
            ),
        )

    def __str__(self):
        return f"{self.reminder_title} - {self.customer.name}"

    def soft_delete(self):
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=("is_deleted", "deleted_at", "updated_at"))
