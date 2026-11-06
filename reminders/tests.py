from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from customers.models import Customer

from .models import Reminder


class ReminderApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            email="reminders-admin@example.com",
            password="Strong-test-password-123!",
        )
        cls.customer = Customer.objects.create(
            name="Reminder Customer",
            email="reminder-customer@example.com",
            phone="0500000000",
        )
        cls.other_customer = Customer.objects.create(
            name="Other Reminder Customer",
            email="other-reminder@example.com",
            phone="0500000001",
        )

    def setUp(self):
        self.client = APIClient()

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def payload(self):
        return {
            "reminder_title": "Trade License Renewal",
            "due_date": (date.today() + timedelta(days=30)).isoformat(),
            "customer": self.customer.id,
            "notes": "Contact customer before due date",
        }

    def test_anonymous_reminder_list_is_rejected(self):
        response = self.client.get("/api/reminders/")

        self.assertEqual(response.status_code, 401)

    def test_admin_can_create_and_list_reminder_fields(self):
        self.authenticate()

        response = self.client.post("/api/reminders/", self.payload(), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["reminder_title"], "Trade License Renewal")
        self.assertEqual(response.data["customer_name"], self.customer.name)
        self.assertEqual(set(response.data), {"id", "reminder_title", "due_date", "customer", "customer_name", "notes", "created_at", "updated_at"})

    def test_filters_support_due_range_and_customer(self):
        self.authenticate()
        self.client.post("/api/reminders/", self.payload(), format="json")
        other_payload = self.payload()
        other_payload.update({"reminder_title": "Passport Renewal", "customer": self.other_customer.id, "due_date": (date.today() + timedelta(days=90)).isoformat()})
        self.client.post("/api/reminders/", other_payload, format="json")

        response = self.client.get(
            "/api/reminders/",
            {"due_from": (date.today() + timedelta(days=20)).isoformat(), "due_to": (date.today() + timedelta(days=40)).isoformat(), "customer": self.customer.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["reminder_title"], "Trade License Renewal")

    def test_admin_can_update_and_soft_delete_reminder(self):
        self.authenticate()
        create_response = self.client.post("/api/reminders/", self.payload(), format="json")
        reminder_id = create_response.data["id"]

        update_response = self.client.patch(
            f"/api/reminders/{reminder_id}/",
            {"reminder_title": "Updated Renewal", "due_date": date.today().isoformat()},
            format="json",
        )
        delete_response = self.client.delete(f"/api/reminders/{reminder_id}/")

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data["reminder_title"], "Updated Renewal")
        self.assertEqual(delete_response.status_code, 204)
        reminder = Reminder.objects.get(pk=reminder_id)
        self.assertTrue(reminder.is_deleted)
        self.assertEqual(self.client.get("/api/reminders/").data, [])
