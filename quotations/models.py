from decimal import Decimal

from django.db import models
from django.utils import timezone

from customers.models import Customer
from services.models import Service


class Quotation(models.Model):
    quotation_number_value = models.PositiveIntegerField(
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )
    quotation_date = models.DateField()
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="quotations",
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "-id")

    def __str__(self):
        return self.quotation_number

    @property
    def quotation_number(self):
        value = self.quotation_number_value or self.pk
        return f"{value:03d}" if value is not None else ""

    def recalculate_totals(self, *, save=True):
        self.subtotal = sum(
            (item.line_total for item in self.items.all()),
            Decimal("0.00"),
        )
        self.total_amount = self.subtotal - self.discount_amount
        if save:
            self.save(update_fields=("subtotal", "total_amount", "updated_at"))

    def soft_delete(self):
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=("is_deleted", "deleted_at", "updated_at"))


class QuotationNumberSequence(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    next_number = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Next quotation number: {self.next_number}"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name="items",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="quotation_items",
    )
    description = models.TextField(blank=True)
    government_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    quantity = models.PositiveIntegerField(default=1)
    start_date = models.DateField()
    end_date = models.DateField()
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
    )

    class Meta:
        ordering = ("id",)

    def save(self, *args, **kwargs):
        self.line_total = (self.government_fee + self.service_fee) * self.quantity
        super().save(*args, **kwargs)
