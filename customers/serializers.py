from rest_framework import serializers

from .models import Customer


class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "bank_name",
            "account_holder_name",
            "account_number",
            "swift_address",
            "iban",
            "trn",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CustomerDetailSerializer(CustomerCreateSerializer):
    pass


class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at", "updated_at")
        read_only_fields = fields
