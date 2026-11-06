from django.urls import path

from .views import QuotationDetailView, QuotationListCreateView


app_name = "quotations"

urlpatterns = [
    path("", QuotationListCreateView.as_view(), name="quotation-list-create"),
    path("<int:pk>/", QuotationDetailView.as_view(), name="quotation-detail"),
]
