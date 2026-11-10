from django.apps import AppConfig


class GovernmentInvoicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "government_invoices"

    def ready(self):
        from . import signals  # noqa: F401
