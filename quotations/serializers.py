from django.db import transaction
from rest_framework import serializers

from customers.models import Customer
from services.models import Service

from .models import Quotation, QuotationItem, QuotationNumberSequence


class QuotationItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = QuotationItem
        fields = (
            "id",
            "service",
            "service_name",
            "description",
            "government_fee",
            "service_fee",
            "quantity",
            "start_date",
            "end_date",
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
        if attrs.get("government_fee", 0) < 0:
            raise serializers.ValidationError({"government_fee": "Government fee cannot be negative."})
        if attrs.get("service_fee", 0) < 0:
            raise serializers.ValidationError({"service_fee": "Service fee cannot be negative."})
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "End date cannot be before the start date."})
        return attrs


class QuotationSerializer(serializers.ModelSerializer):
    quotation_number = serializers.SerializerMethodField()
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.filter(is_deleted=False))
    items = QuotationItemSerializer(many=True)

    class Meta:
        model = Quotation
        fields = (
            "id",
            "quotation_number",
            "quotation_date",
            "customer",
            "customer_name",
            "customer_email",
            "items",
            "subtotal",
            "discount_amount",
            "total_amount",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "quotation_number",
            "customer_name",
            "customer_email",
            "subtotal",
            "total_amount",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        if attrs.get("discount_amount", 0) < 0:
            raise serializers.ValidationError({"discount_amount": "Discount amount cannot be negative."})
        if attrs.get("items") is not None and not attrs["items"]:
            raise serializers.ValidationError({"items": "Add at least one service."})
        return attrs

    def get_quotation_number(self, obj):
        return obj.quotation_number

    def _validate_and_recalculate(self, quotation):
        quotation.recalculate_totals()
        if quotation.discount_amount > quotation.subtotal:
            raise serializers.ValidationError({"discount_amount": "Discount cannot be greater than the subtotal."})
        quotation.recalculate_totals()

    def _create_items(self, quotation, items_data):
        for item_data in items_data:
            QuotationItem.objects.create(quotation=quotation, **item_data)

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        sequence = QuotationNumberSequence.objects.select_for_update().get(pk=1)
        number = max(1, sequence.next_number)
        sequence.next_number = number + 1
        sequence.save(update_fields=("next_number",))
        quotation = Quotation.objects.create(quotation_number_value=number, **validated_data)
        self._create_items(quotation, items_data)
        self._validate_and_recalculate(quotation)
        return quotation

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
