from django.contrib import admin

from .models import CustomerDocument


@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ("document_title", "expiry_date", "customer", "is_deleted")
    list_filter = ("expiry_date", "is_deleted")
    search_fields = ("document_title", "customer__name", "customer__email")
