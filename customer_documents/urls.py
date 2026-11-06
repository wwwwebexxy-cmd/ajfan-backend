from django.urls import path

from .views import CustomerDocumentDetailView, CustomerDocumentListCreateView


app_name = "customer-documents"

urlpatterns = [
    path("", CustomerDocumentListCreateView.as_view(), name="document-list-create"),
    path("<int:pk>/", CustomerDocumentDetailView.as_view(), name="document-detail"),
]
