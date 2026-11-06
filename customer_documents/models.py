from django.db import models
from django.utils import timezone

from customers.models import Customer


class CustomerDocument(models.Model):
    document_title = models.CharField(max_length=180)
    expiry_date = models.DateField()
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="documents",
    )
    notes = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("expiry_date", "document_title", "id")

    def __str__(self):
        return f"{self.document_title} - {self.customer.name}"

    def soft_delete(self):
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=("is_deleted", "deleted_at", "updated_at"))
