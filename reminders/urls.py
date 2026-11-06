from django.urls import path

from .views import ReminderDetailView, ReminderListCreateView


app_name = "reminders"

urlpatterns = [
    path("", ReminderListCreateView.as_view(), name="reminder-list-create"),
    path("<int:pk>/", ReminderDetailView.as_view(), name="reminder-detail"),
]
