from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

User = get_user_model()


class AccountAPISecurityTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="Safe-Test-Password-123")
        self.other_user = User.objects.create_user(email="other@example.com", password="Safe-Test-Password-456")

    def test_regular_user_only_sees_their_own_account(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/accounts/")
        self.assertEqual(response.status_code, 200)
        results = response.data.get("results", response.data)
        self.assertEqual([item["email"] for item in results], [self.user.email])

    def test_regular_user_cannot_retrieve_another_account(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/accounts/{self.other_user.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_public_registration_is_disabled_by_default(self):
        with override_settings(ENABLE_PUBLIC_REGISTRATION=False):
            response = self.client.post("/api/accounts/", {"email": "new@example.com"}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_regular_user_cannot_delete_accounts(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/accounts/{self.other_user.pk}/")
        self.assertIn(response.status_code, (403, 404))

