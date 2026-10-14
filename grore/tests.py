"""Project-level tests: i18n URL routing, the language switch, and an admin
smoke test."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from images.models import Image
from images.tests import make_image_file
from pages.models import Page


class I18nRoutingTests(TestCase):
    def test_root_redirects_to_default_language(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp["Location"].startswith("/fr/"))

    def test_both_language_prefixes_serve_the_gallery(self):
        self.assertEqual(self.client.get("/fr/").status_code, 200)
        self.assertEqual(self.client.get("/en/").status_code, 200)

    def test_set_language_switches_active_locale(self):
        resp = self.client.post(
            reverse("set_language"), {"language": "en", "next": "/fr/"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.client.get("/").get("Location"), "/en/")


class AdminSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser(
            "admin", "admin@example.com", "passphrase-123")

    def setUp(self):
        self.client.force_login(self.admin)

    def test_admin_index_ok(self):
        self.assertEqual(self.client.get("/admin/").status_code, 200)

    def test_image_changelist_ok(self):
        Image.objects.create(
            identifier="a", slug="a", pub_date=timezone.now(),
            modif_date=timezone.now(), file=make_image_file())
        self.assertEqual(
            self.client.get("/admin/images/image/").status_code, 200)

    def test_image_change_page_ok(self):
        img = Image.objects.create(
            identifier="a", slug="a", pub_date=timezone.now(),
            modif_date=timezone.now(), file=make_image_file())
        self.assertEqual(
            self.client.get(f"/admin/images/image/{img.pk}/change/").status_code, 200)

    def test_image_add_page_ok(self):
        self.assertEqual(
            self.client.get("/admin/images/image/add/").status_code, 200)

    def test_page_changelist_ok(self):
        Page.objects.create(slug="p", title="P", content="x",
                            pub_date=timezone.now())
        self.assertEqual(
            self.client.get("/admin/pages/page/").status_code, 200)
