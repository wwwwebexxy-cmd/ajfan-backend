from rest_framework import serializers

from customers.models import Customer

from .models import CustomerDocument


class CustomerDocumentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.filter(is_deleted=False),
    )

    class Meta:
        model = CustomerDocument
        fields = (
            "id",
            "document_title",
            "expiry_date",
            "customer",
            "customer_name",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "customer_name", "created_at", "updated_at")

    def validate_document_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Document title cannot be empty.")
        return value.strip()
