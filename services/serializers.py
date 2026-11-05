from rest_framework import serializers

from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "image",
            "service_charge",
            "includes_government_fee",
            "government_fee",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_service_charge(self, value):
        if value < 0:
            raise serializers.ValidationError("Service charge cannot be negative.")
        return value

    def validate_government_fee(self, value):
        if value < 0:
            raise serializers.ValidationError("Government fee cannot be negative.")
        return value
