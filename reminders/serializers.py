from rest_framework import serializers

from customers.models import Customer

from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.filter(is_deleted=False))

    class Meta:
        model = Reminder
        fields = (
            "id",
            "reminder_title",
            "due_date",
            "customer",
            "customer_name",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "customer_name", "created_at", "updated_at")

    def validate_reminder_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Reminder title cannot be empty.")
        return value.strip()
