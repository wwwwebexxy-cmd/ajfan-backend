from django.db import models
from django.utils import timezone


class Service(models.Model):
    name = models.CharField(max_length=180)
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2)
    includes_government_fee = models.BooleanField(default=False)
    government_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "-id")

    def __str__(self):
        return self.name

    def soft_delete(self):
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=("is_deleted", "deleted_at", "updated_at"))
