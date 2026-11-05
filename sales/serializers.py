from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from customers.models import Customer
from services.models import Service

from .models import InvoiceNumberSequence, SalesInvoice, SalesInvoiceItem


User = get_user_model()


class StaffSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "name")
        read_only_fields = fields

    def get_name(self, obj):
        first_name = getattr(obj, "first_name", "")
        last_name = getattr(obj, "last_name", "")
        return " ".join(part for part in (first_name, last_name) if part) or obj.email


class SalesInvoiceItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = SalesInvoiceItem
        fields = (
            "id",
            "service",
            "service_name",
            "description",
            "sub_fee",
            "service_fee",
            "quantity",
            "start_date",
            "expiry_date",
            "line_total",
        )
        read_only_fields = ("id", "service_name", "line_total")

    def validate_service(self, value):
        if value.is_deleted:
            raise serializers.ValidationError("This service is no longer available.")
        return value

    def validate(self, attrs):
        if attrs.get("quantity", 1) < 1:
            raise serializers.ValidationError({"quantity": "Quantity must be at least 1."})
        if attrs.get("sub_fee", 0) < 0:
            raise serializers.ValidationError({"sub_fee": "Sub fee cannot be negative."})
        if attrs.get("service_fee", 0) < 0:
            raise serializers.ValidationError({"service_fee": "Service fee cannot be negative."})
        start_date = attrs.get("start_date")
        expiry_date = attrs.get("expiry_date")
        if start_date and expiry_date and expiry_date < start_date:
            raise serializers.ValidationError(
                {"expiry_date": "Expiry date cannot be before the start date."}
            )
        return attrs


class SalesInvoiceSerializer(serializers.ModelSerializer):
    invoice_number = serializers.SerializerMethodField()
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)
    staff_name = serializers.SerializerMethodField()
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.filter(is_deleted=False)
    )
    staff = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=True, is_active=True),
        allow_null=True,
        required=False,
    )
    items = SalesInvoiceItemSerializer(many=True)

    class Meta:
        model = SalesInvoice
        fields = (
            "id",
            "invoice_number",
            "invoice_date",
            "customer",
            "customer_name",
            "customer_email",
            "items",
            "subtotal",
            "discount_amount",
            "total_amount",
            "received_amount",
            "balance_amount",
            "payment_mode",
            "paid_by_staff",
            "staff",
            "staff_name",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "invoice_number",
            "customer_name",
            "customer_email",
            "subtotal",
            "total_amount",
            "balance_amount",
            "staff_name",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        if attrs.get("discount_amount", 0) < 0:
            raise serializers.ValidationError(
                {"discount_amount": "Discount amount cannot be negative."}
            )
        if attrs.get("received_amount", 0) < 0:
            raise serializers.ValidationError(
                {"received_amount": "Received amount cannot be negative."}
            )
        items = attrs.get("items")
        if items is not None and not items:
            raise serializers.ValidationError({"items": "Add at least one service."})
        if attrs.get("paid_by_staff") and not attrs.get("staff"):
            raise serializers.ValidationError(
                {"staff": "Select a staff member when paid by staff is enabled."}
            )
        return attrs

    def get_staff_name(self, obj):
        if not obj.staff:
            return ""
        first_name = getattr(obj.staff, "first_name", "")
        last_name = getattr(obj.staff, "last_name", "")
        return " ".join(part for part in (first_name, last_name) if part) or obj.staff.email

    def get_invoice_number(self, obj):
        return obj.invoice_number

    def _validate_and_recalculate(self, invoice):
        if invoice.paid_by_staff and invoice.staff_id is None:
            raise serializers.ValidationError(
                {"staff": "Select a staff member when paid by staff is enabled."}
            )
        invoice.recalculate_totals()
        if invoice.discount_amount > invoice.subtotal:
            raise serializers.ValidationError(
                {"discount_amount": "Discount cannot be greater than the subtotal."}
            )
        if invoice.received_amount > invoice.total_amount:
            raise serializers.ValidationError(
                {"received_amount": "Received amount cannot be greater than the total."}
            )
        invoice.recalculate_totals()

    def _create_items(self, invoice, items_data):
        for item_data in items_data:
            SalesInvoiceItem.objects.create(invoice=invoice, **item_data)

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        sequence = InvoiceNumberSequence.objects.select_for_update().get(pk=1)
        number = max(1, sequence.next_number)
        sequence.next_number = number + 1
        sequence.save(update_fields=("next_number",))
        invoice = SalesInvoice.objects.create(
            invoice_number_value=number,
            **validated_data,
        )
        self._create_items(invoice, items_data)
        self._validate_and_recalculate(invoice)
        return invoice

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            self._create_items(instance, items_data)
        self._validate_and_recalculate(instance)
        return instance
