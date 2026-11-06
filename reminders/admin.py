from django.contrib import admin

from .models import Reminder


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("reminder_title", "due_date", "customer", "is_deleted")
    list_filter = ("due_date", "is_deleted")
    search_fields = ("reminder_title", "customer__name", "customer__email")
