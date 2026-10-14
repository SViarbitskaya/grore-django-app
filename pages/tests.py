"""Tests for the pages app: the flat-page model, its detail view, the static
contact page, i18n URL prefixing and translated fields."""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone, translation

from .models import Page


def make_page(slug="apropos", title="A propos", content="<p>Bonjour le monde</p>"):
    return Page.objects.create(
        slug=slug, title=title, content=content, pub_date=timezone.now())


class PageModelTests(TestCase):
    def test_str_is_title(self):
        self.assertEqual(str(make_page(title="Mentions")), "Mentions")

    def test_get_absolute_url_is_language_prefixed(self):
        page = make_page(slug="apropos")
        with translation.override("fr"):
            self.assertEqual(page.get_absolute_url(), "/fr/apropos/")
        with translation.override("en"):
            self.assertEqual(page.get_absolute_url(), "/en/apropos/")

    def test_title_and_content_are_translated_per_language(self):
        page = Page(slug="p", pub_date=timezone.now())
        page.title_fr, page.title_en = "Titre", "Title"
        page.content_fr, page.content_en = "<p>fr</p>", "<p>en</p>"
        page.save()
        with translation.override("fr"):
            fresh = Page.objects.get(pk=page.pk)
            self.assertEqual(fresh.title, "Titre")
            self.assertEqual(fresh.content, "<p>fr</p>")
        with translation.override("en"):
            fresh = Page.objects.get(pk=page.pk)
            self.assertEqual(fresh.title, "Title")


class PageViewTests(TestCase):
    def test_page_renders_title_and_raw_content(self):
        make_page(title="A propos", content="<p>Bonjour le monde</p>")
        resp = self.client.get("/fr/apropos/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "page.html")
        self.assertTemplateUsed(resp, "base.html")
        self.assertContains(resp, "A propos")
        self.assertContains(resp, "<p>Bonjour le monde</p>", html=False)

    def test_unknown_slug_is_404(self):
        self.assertEqual(self.client.get("/fr/does-not-exist/").status_code, 404)

    def test_missing_language_prefix_redirects_to_default(self):
        make_page(slug="apropos")
        resp = self.client.get("/apropos/")
        self.assertRedirects(resp, "/fr/apropos/",
                             status_code=302, target_status_code=200)


class ContactPageTests(TestCase):
    def test_contact_page_ok(self):
        resp = self.client.get("/fr/contact/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "contact.html")
        self.assertTemplateUsed(resp, "base.html")

    def test_contact_available_in_english(self):
        self.assertEqual(self.client.get("/en/contact/").status_code, 200)

    def test_contact_missing_prefix_redirects(self):
        resp = self.client.get("/contact/")
        self.assertRedirects(resp, "/fr/contact/",
                             status_code=302, target_status_code=200)
