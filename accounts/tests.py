from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AdminLoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email = "admin@example.com"
        cls.password = "Strong-test-password-123!"
        get_user_model().objects.create_superuser(
            email=cls.email,
            password=cls.password,
        )

    def test_admin_path_redirects_anonymous_user_to_login(self):
        response = self.client.get("/ajifan-documents/", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log in")
        self.assertIn("/ajifan-documents/login/", response.redirect_chain[-1][0])

    def test_admin_accepts_email_and_password(self):
        response = self.client.post(
            reverse("admin:login"),
            {"username": self.email, "password": self.password},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_default_admin_path_is_not_exposed(self):
        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 404)
