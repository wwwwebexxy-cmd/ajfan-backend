from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("ajifan-documents/", admin.site.urls),
    path("api/customers/", include("customers.urls")),
]
