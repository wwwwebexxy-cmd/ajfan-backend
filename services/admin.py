from django.contrib import admin
from django.utils import timezone

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "service_charge", "government_fee", "is_deleted", "created_at")
    list_filter = ("includes_government_fee", "is_deleted")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at", "deleted_at")

    def delete_model(self, request, obj):
        obj.soft_delete()

    def delete_queryset(self, request, queryset):
        queryset.update(is_deleted=True, deleted_at=timezone.now())
