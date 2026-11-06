from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path


urlpatterns = [
    path("ajifan-documents/", admin.site.urls),
    path("api/customers/", include("customers.urls")),
    path("api/services/", include("services.urls")),
    path("api/sales-invoices/", include("sales.urls")),
    path("api/government-invoices/", include("government_invoices.urls")),
    path("api/quotations/", include("quotations.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
