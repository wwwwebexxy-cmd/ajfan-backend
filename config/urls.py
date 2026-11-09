from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.views.generic import RedirectView


urlpatterns = [
    path("ajfan-documents/", admin.site.urls),
    re_path(r"^ajifan-documents/?(?P<path>.*)$", RedirectView.as_view(url="/ajfan-documents/%(path)s", permanent=True)),
    path("api/customers/", include("customers.urls")),
    path("api/services/", include("services.urls")),
    path("api/sales-invoices/", include("sales.urls")),
    path("api/government-invoices/", include("government_invoices.urls")),
    path("api/quotations/", include("quotations.urls")),
    path("api/customer-documents/", include("customer_documents.urls")),
    path("api/reminders/", include("reminders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
