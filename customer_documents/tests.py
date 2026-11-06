from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from customers.models import Customer
from reminders.models import Reminder

from .models import CustomerDocument


class CustomerDocumentApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            email="documents-admin@example.com",
            password="Strong-test-password-123!",
        )
        cls.customer = Customer.objects.create(
            name="Document Customer",
            email="document-customer@example.com",
            phone="0500000000",
        )
        cls.other_customer = Customer.objects.create(
            name="Other Customer",
            email="other-customer@example.com",
            phone="0500000001",
        )

    def setUp(self):
        self.client = APIClient()

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def payload(self):
        return {
            "document_title": "Trade License",
            "expiry_date": (date.today() + timedelta(days=30)).isoformat(),
            "customer": self.customer.id,
            "notes": "Renew before expiry",
        }

    def test_anonymous_document_list_is_rejected(self):
        response = self.client.get("/api/customer-documents/")

        self.assertEqual(response.status_code, 401)

    def test_admin_can_create_and_list_document_fields(self):
        self.authenticate()

        response = self.client.post("/api/customer-documents/", self.payload(), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["document_title"], "Trade License")
        self.assertEqual(response.data["customer_name"], self.customer.name)
        self.assertEqual(set(response.data), {"id", "document_title", "expiry_date", "customer", "customer_name", "notes", "created_at", "updated_at"})

    def test_filters_support_expiry_range_and_customer(self):
        self.authenticate()
        self.client.post("/api/customer-documents/", self.payload(), format="json")
        other_payload = self.payload()
        other_payload.update({"document_title": "Passport", "customer": self.other_customer.id, "expiry_date": (date.today() + timedelta(days=90)).isoformat()})
        self.client.post("/api/customer-documents/", other_payload, format="json")

        response = self.client.get(
            "/api/customer-documents/",
            {"expiry_from": (date.today() + timedelta(days=20)).isoformat(), "expiry_to": (date.today() + timedelta(days=40)).isoformat(), "customer": self.customer.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["document_title"], "Trade License")

    def test_admin_can_update_and_soft_delete_document(self):
        self.authenticate()
        create_response = self.client.post("/api/customer-documents/", self.payload(), format="json")
        document_id = create_response.data["id"]

        update_response = self.client.patch(
            f"/api/customer-documents/{document_id}/",
            {"document_title": "Updated Trade License", "expiry_date": date.today().isoformat()},
            format="json",
        )
        delete_response = self.client.delete(f"/api/customer-documents/{document_id}/")

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data["document_title"], "Updated Trade License")
        self.assertEqual(delete_response.status_code, 204)
        document = CustomerDocument.objects.get(pk=document_id)
        self.assertTrue(document.is_deleted)
        self.assertEqual(self.client.get("/api/customer-documents/").data, [])

    def test_document_creates_reminder_ten_days_before_expiry(self):
        self.authenticate()

        response = self.client.post("/api/customer-documents/", self.payload(), format="json")

        self.assertEqual(response.status_code, 201)
        document = CustomerDocument.objects.get(pk=response.data["id"])
        reminder = Reminder.objects.get(source_document=document)
        self.assertEqual(reminder.due_date, document.expiry_date - timedelta(days=10))
        self.assertEqual(reminder.reminder_title, "Document expiry: Trade License")

    def test_document_expiry_update_syncs_the_same_reminder(self):
        self.authenticate()
        create_response = self.client.post("/api/customer-documents/", self.payload(), format="json")
        document_id = create_response.data["id"]
        original_reminder = Reminder.objects.get(source_document_id=document_id)
        new_expiry = date.today() + timedelta(days=120)

        response = self.client.patch(
            f"/api/customer-documents/{document_id}/",
            {"expiry_date": new_expiry.isoformat()},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        reminder = Reminder.objects.get(source_document_id=document_id)
        self.assertEqual(reminder.id, original_reminder.id)
        self.assertEqual(reminder.due_date, new_expiry - timedelta(days=10))

    def test_deleting_document_deactivates_its_automatic_reminder(self):
        self.authenticate()
        create_response = self.client.post("/api/customer-documents/", self.payload(), format="json")
        document_id = create_response.data["id"]

        response = self.client.delete(f"/api/customer-documents/{document_id}/")

        self.assertEqual(response.status_code, 204)
        reminder = Reminder.objects.get(source_document_id=document_id)
        self.assertTrue(reminder.is_deleted)
