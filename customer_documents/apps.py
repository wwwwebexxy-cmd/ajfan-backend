from django.apps import AppConfig


class CustomerDocumentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "customer_documents"

    def ready(self):
        from . import signals  # noqa: F401
