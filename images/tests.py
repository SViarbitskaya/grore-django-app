"""Tests for the images app: model helpers, gallery/HTMX view, search,
the session-based selection cart, zip downloads and navigation."""

import io
import json
import os
import shutil
import tempfile
import zipfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone, translation

from PIL import Image as PILImage

from pages.models import Page

from .forms import ImageSearchForm
from .mixins import SelectionMixin
from .models import Image
from .text_cleaning import strip_ethnic_type_descriptors


def make_image_file(name="test.png", color=(200, 30, 30)):
    """A real (tiny) PNG so ImageField validation and Pillow are both happy."""
    buf = io.BytesIO()
    PILImage.new("RGB", (8, 8), color).save(buf, format="PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


def create_image(note="Une image", identifier=None, slug=None, with_thumbnail=False,
                 with_zoom=False, high_res=False, **extra):
    identifier = identifier or f"img-{Image.objects.count() + 1}"
    slug = slug if slug is not None else identifier
    now = timezone.now()
    img = Image(
        identifier=identifier, slug=slug, note=note,
        pub_date=now, modif_date=now, high_res=high_res, **extra,
    )
    img.file = make_image_file(f"{identifier}.png")
    if with_thumbnail:
        img.thumbnail = make_image_file(f"{identifier}-thumb.png")
    if with_zoom:
        img.zoom = make_image_file(f"{identifier}-zoom.png")
    img.save()
    return img


class MediaTestCase(TestCase):
    """Base class: isolate every test's uploads in a throwaway MEDIA_ROOT and
    pin the active language so reverse() yields the /fr/ prefixed URLs."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media_root = tempfile.mkdtemp(prefix="grore-test-media-")
        cls._media_override = override_settings(MEDIA_ROOT=cls._media_root)
        cls._media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._media_override.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        translation.activate("fr")
        self.addCleanup(translation.deactivate)


class ImageModelTests(MediaTestCase):
    def test_filename_returns_basename_only(self):
        img = create_image(identifier="abc")
        self.assertEqual(img.filename(), os.path.basename(img.file.name))
        self.assertNotIn("/", img.filename())
        self.assertTrue(img.filename().endswith(".png"))

    def test_thumbnail_preview_is_empty_without_thumbnail(self):
        self.assertEqual(create_image().thumbnail_preview(), "")

    def test_thumbnail_preview_renders_img_tag_when_present(self):
        img = create_image(with_thumbnail=True)
        preview = img.thumbnail_preview()
        self.assertIn("<img", preview)
        self.assertIn(img.thumbnail.url, preview)

    def test_flag_defaults(self):
        img = create_image()
        self.assertFalse(img.high_res)
        self.assertFalse(img.ai_gen)

    def test_slug_must_be_unique(self):
        create_image(identifier="one", slug="dup")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_image(identifier="two", slug="dup")

    def test_note_is_translated_per_language(self):
        img = Image(identifier="i18n", slug="i18n", pub_date=timezone.now(),
                    modif_date=timezone.now())
        img.file = make_image_file()
        img.note_fr = "bonjour"
        img.note_en = "hello"
        img.save()
        with translation.override("fr"):
            self.assertEqual(Image.objects.get(pk=img.pk).note, "bonjour")
        with translation.override("en"):
            self.assertEqual(Image.objects.get(pk=img.pk).note, "hello")


class ImageSearchFormTests(TestCase):
    def test_blank_query_is_valid(self):
        self.assertTrue(ImageSearchForm(data={"search_query": ""}).is_valid())

    def test_query_within_limit_is_valid(self):
        self.assertTrue(ImageSearchForm(data={"search_query": "x" * 100}).is_valid())

    def test_query_over_limit_is_invalid(self):
        form = ImageSearchForm(data={"search_query": "x" * 101})
        self.assertFalse(form.is_valid())
        self.assertIn("search_query", form.errors)


class StripEthnicTypeDescriptorsTests(TestCase):
    """strip_ethnic_type_descriptors(): the caption-cleanup Philippe Mairesse
    requested on 2026-09-18 ('suppress the existing discriminating terms')."""

    def test_strips_fr_de_type_africain(self):
        self.assertEqual(
            strip_ethnic_type_descriptors("Visage d’homme de type africain. Image abîmée."),
            "Visage d’homme. Image abîmée.")

    def test_strips_fr_de_type_maghrebin_plural(self):
        self.assertEqual(
            strip_ethnic_type_descriptors("Jeunes hommes de type maghrébin dans la rue la nuit."),
            "Jeunes hommes dans la rue la nuit.")

    def test_strips_fr_de_type_asiatique_and_is_case_insensitive(self):
        self.assertEqual(
            strip_ethnic_type_descriptors("Visage DE TYPE Asiatique. Noir et blanc."),
            "Visage. Noir et blanc.")

    def test_strips_fr_leftover_comma_before_period(self):
        # The classification clause sat right before the sentence-ending
        # period, behind a comma introducing it: both must go together.
        self.assertEqual(
            strip_ethnic_type_descriptors(
                "Visage d’un couple, homme et femme, de type maghrébin. Image abîmée."),
            "Visage d’un couple, homme et femme. Image abîmée.")

    def test_strips_en_bare_ethnicity_type(self):
        self.assertEqual(
            strip_ethnic_type_descriptors("African type man with glasses and bow tie."),
            "Man with glasses and bow tie.")

    def test_strips_en_north_african_type(self):
        self.assertEqual(
            strip_ethnic_type_descriptors("North African type man sitting with a cigarette."),
            "Man sitting with a cigarette.")

    def test_strips_en_hyphenated_ethnicity_type(self):
        # Regression test: the original regex only matched a space between
        # the ethnicity word and "type" and missed this hyphenated form
        # (found in X2249X's note_en after the first cleanup pass).
        self.assertEqual(
            strip_ethnic_type_descriptors("Two African-type children sitting on a bed."),
            "Two children sitting on a bed.")

    def test_fixes_article_left_stranded_by_removal(self):
        # "an African type man" -> "an man" would be broken; must read "a man".
        self.assertEqual(
            strip_ethnic_type_descriptors("Face of an African type man. Damaged image."),
            "Face of a man. Damaged image.")

    def test_keeps_of_before_a_bare_type_phrase(self):
        # "of" belongs to "Face of ...", not to the discriminating clause.
        self.assertEqual(
            strip_ethnic_type_descriptors("Face of African type man with suit and white tie."),
            "Face of man with suit and white tie.")

    def test_removes_of_type_when_it_is_itself_the_predicate(self):
        self.assertEqual(
            strip_ethnic_type_descriptors("Two young men of North African type are walking in the street."),
            "Two young men are walking in the street.")

    def test_recapitalizes_when_removal_was_at_sentence_start(self):
        self.assertEqual(
            strip_ethnic_type_descriptors("African type face and striped polo shirt."),
            "Face and striped polo shirt.")

    def test_leaves_unrelated_text_untouched(self):
        note = "Un chat noir sur le toit."
        self.assertEqual(strip_ethnic_type_descriptors(note), note)

    def test_leaves_none_and_empty_string_untouched(self):
        self.assertIsNone(strip_ethnic_type_descriptors(None))
        self.assertEqual(strip_ethnic_type_descriptors(""), "")


class HomeViewTests(MediaTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("home")

    def test_homepage_ok_and_uses_full_template(self):
        create_image()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "images/index.html")
        self.assertTemplateUsed(resp, "base.html")

    def test_htmx_request_uses_partial_only(self):
        create_image()
        resp = self.client.get(self.url, headers={"hx-request": "true"})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "images/htmx_partial.html")
        self.assertTemplateNotUsed(resp, "base.html")

    def test_lists_all_images_when_no_search(self):
        for i in range(5):
            create_image(identifier=f"n{i}")
        resp = self.client.get(self.url)
        self.assertEqual(len(resp.context["images"]), 5)

    def test_search_matches_whole_word_case_insensitively(self):
        hit = create_image(note="Un chat noir sur le toit", identifier="a")
        create_image(note="Le chien aboie", identifier="b")
        create_image(note="Un chaton joueur", identifier="c")  # substring, not a word
        create_image(note="Chateau fort", identifier="d")      # substring, not a word

        for query in ("chat", "CHAT", "Chat"):
            resp = self.client.get(self.url, {"search_query": query})
            notes = {img.note for img in resp.context["images"]}
            self.assertEqual(notes, {hit.note}, f"query={query!r}")

    def test_search_requires_all_terms_to_match(self):
        both = create_image(note="Un chat et un chien", identifier="a")
        create_image(note="Un chat seul", identifier="b")
        create_image(note="Un chien seul", identifier="c")
        resp = self.client.get(self.url, {"search_query": "chat chien"})
        self.assertEqual({i.note for i in resp.context["images"]}, {both.note})

    def test_common_connector_word_does_not_flood_multiword_search(self):
        # Regression test: "maillot de bains" (Philippe Mairesse, 2026-08-19)
        # used to match nearly everything because "de" alone satisfied the
        # OR-based term match, while "maillot" alone worked fine.
        hit = create_image(note="Femme en maillot de bains sur la plage", identifier="a")
        create_image(note="Un chat noir de type gouttiere", identifier="b")  # contains "de", not "maillot"
        create_image(note="Un maillot de sport rouge", identifier="c")  # "maillot" and "de", not "bains"
        resp = self.client.get(self.url, {"search_query": "maillot de bains"})
        self.assertEqual({i.note for i in resp.context["images"]}, {hit.note})

    def test_search_with_no_match_is_empty(self):
        create_image(note="Un chat noir")
        resp = self.client.get(self.url, {"search_query": "zzz"})
        self.assertEqual(list(resp.context["images"]), [])

    def test_search_is_robust_to_empty_and_untranslated_notes(self):
        # Saved with no note at all: base note -> '', both translations NULL.
        blank = Image(identifier="blank", slug="blank",
                      pub_date=timezone.now(), modif_date=timezone.now())
        blank.file = make_image_file()
        blank.save()
        # Saved with only the French note populated (note_en stays NULL).
        fr_only = Image(identifier="fronly", slug="fronly",
                        pub_date=timezone.now(), modif_date=timezone.now())
        fr_only.file = make_image_file()
        fr_only.note_fr = "Un chat noir"
        fr_only.save()
        match = create_image(note="Le chat dort", identifier="match")

        for prefix in ("/fr/", "/en/"):
            resp = self.client.get(prefix, {"search_query": "chat"})
            self.assertEqual(resp.status_code, 200, prefix)

        resp = self.client.get("/fr/", {"search_query": "chat"})
        self.assertEqual({i.pk for i in resp.context["images"]},
                         {fr_only.pk, match.pk})

    def test_pagination_caps_first_page_at_paginate_by(self):
        for i in range(20):
            create_image(identifier=f"p{i}")
        resp = self.client.get(self.url)
        self.assertEqual(len(resp.context["images"]), 15)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(resp.context["page_obj"].has_next())

    def test_selected_ids_parsed_from_session_and_bad_values_skipped(self):
        session = self.client.session
        session["selected_images"] = ["1", "not-a-number", None, 3]
        session.save()
        resp = self.client.get(self.url)
        self.assertEqual(resp.context["selected_images_ids"], [1, 3])

    def test_context_exposes_search_form_and_language(self):
        resp = self.client.get(self.url)
        self.assertIsInstance(resp.context["search_form"], ImageSearchForm)
        self.assertEqual(resp.context["language"], "fr")

    def test_calculated_height_tracks_page_number(self):
        for i in range(20):
            create_image(identifier=f"h{i}")
        resp = self.client.get(self.url, {"page": 2})
        self.assertEqual(resp.context["calculated_height"], 200)

    def test_high_res_image_with_zoom_renders_zoom_hooks_in_partial(self):
        create_image(high_res=True, with_thumbnail=True, with_zoom=True)
        resp = self.client.get(self.url, headers={"hx-request": "true"})
        self.assertContains(resp, "data-zoom-url")

    def test_mobile_search_bar_is_outside_the_collapse_menu_and_phone_only(self):
        # Regression test: Philippe reported (2026-09-07) that on phones the
        # search box was only reachable behind the hamburger toggle. A
        # dedicated mobile copy (distinct auto_id "mobile_id_search_query")
        # must render before (outside) the collapsible #navbarSupportedContent
        # div, inside a d-lg-none wrapper so it's phone-only.
        create_image()
        resp = self.client.get(self.url)
        content = resp.content.decode()
        self.assertIn("mobile_id_search_query", content)
        collapse_at = content.index('id="navbarSupportedContent"')
        self.assertLess(content.index("mobile_id_search_query"), collapse_at)
        self.assertLess(content.index('class="d-lg-none"'), collapse_at)

    def test_desktop_search_bar_keeps_its_original_position_and_is_desktop_only(self):
        # The desktop search bar (default auto_id "id_search_query") must
        # stay exactly where it always was: inside the collapse, between the
        # nav links and the language switcher, wrapped so phones don't show
        # it a second time when the hamburger menu is opened.
        create_image()
        resp = self.client.get(self.url)
        content = resp.content.decode()
        collapse_at = content.index('id="navbarSupportedContent"')
        nav_links_at = content.index('navbarSupportedContent">') + len('navbarSupportedContent">')
        desktop_wrapper_at = content.index('class="d-none d-lg-block"')
        # The exact quoted id (not a substring of "mobile_id_search_query").
        desktop_search_at = content.index('id="id_search_query"')
        language_switch_at = content.index('class="language-switch"')
        self.assertGreater(desktop_wrapper_at, collapse_at)
        self.assertGreater(desktop_search_at, nav_links_at)
        self.assertLess(desktop_search_at, language_switch_at)


class SelectionMixinUnitTests(TestCase):
    """The branches that the wired-up views can't reach (non-ajax / wrong verb)."""

    def setUp(self):
        self.rf = RequestFactory()
        self.mixin = SelectionMixin()

    def test_update_rejects_non_ajax(self):
        req = self.rf.post("/x")
        req.session = {}
        self.assertEqual(self.mixin.update_session_selection(req),
                         {"status": "Invalid request: not ajax!"})

    def test_update_rejects_non_post_ajax(self):
        req = self.rf.get("/x", headers={"x-requested-with": "XMLHttpRequest"})
        req.session = {}
        self.assertEqual(self.mixin.update_session_selection(req),
                         {"status": "Invalid request: not POST!"})

    def test_is_selected_rejects_non_ajax(self):
        req = self.rf.get("/x")
        req.session = {}
        self.assertEqual(self.mixin.is_selected(req),
                         {"status": "Invalid request: not ajax!"})

    def test_is_selected_rejects_non_get_ajax(self):
        req = self.rf.post("/x", headers={"x-requested-with": "XMLHttpRequest"})
        req.session = {}
        self.assertEqual(self.mixin.is_selected(req),
                         {"status": "Invalid request: not GET!"})

    def test_get_selected_images_filters_by_session_ids(self):
        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            keep = create_image(identifier="keep")
            create_image(identifier="drop")
            req = self.rf.get("/x")
            req.session = {"selected_images": [keep.id]}
            self.assertQuerySetEqual(self.mixin.get_selected_images(req), [keep])

    def test_clear_selection_empties_the_session_list(self):
        req = self.rf.delete("/x")
        req.session = {"selected_images": ["1", "2", "3"]}
        self.mixin.clear_selection(req)
        self.assertEqual(req.session["selected_images"], [])


class ToggleSelectionViewTests(TestCase):
    def setUp(self):
        self.url = reverse("toggle_selection")

    def toggle(self, image_id, action, ajax=True):
        headers = {"x-requested-with": "XMLHttpRequest"} if ajax else {}
        return self.client.post(
            self.url, data=json.dumps({"image_id": image_id, "action": action}),
            content_type="application/json", headers=headers,
        )

    def test_select_then_deselect_round_trip(self):
        resp = self.toggle(7, "select")
        self.assertEqual(resp.json(), {"status": "success", "message": "Image selected."})
        # ids are normalised to strings regardless of the payload type
        self.assertEqual(self.client.session["selected_images"], ["7"])

        resp = self.toggle(7, "select")
        self.assertEqual(resp.json()["message"], "Image already selected.")
        self.assertEqual(self.client.session["selected_images"], ["7"])

        resp = self.toggle(7, "deselect")
        self.assertEqual(resp.json()["message"], "Image deselected.")
        self.assertEqual(self.client.session["selected_images"], [])

        resp = self.toggle(7, "deselect")
        self.assertEqual(resp.json()["message"], "Image was not selected.")

    def test_invalid_action_returns_error(self):
        resp = self.toggle(1, "frobnicate")
        self.assertEqual(resp.json()["status"], "error")

    def test_non_ajax_is_rejected(self):
        resp = self.toggle(1, "select", ajax=False)
        self.assertEqual(resp.json(), {"status": "Invalid request: not ajax!"})


class SelectionCartRoundTripTests(MediaTestCase):
    """End-to-end through the real toggle + delete endpoints (no hand-set
    session), covering the id-type inconsistency between the two views."""

    def toggle(self, image_id, action):
        return self.client.post(
            reverse("toggle_selection"),
            data=json.dumps({"image_id": image_id, "action": action}),
            content_type="application/json",
            headers={"x-requested-with": "XMLHttpRequest"},
        )

    def test_select_via_toggle_then_delete_via_endpoint(self):
        img = create_image(with_thumbnail=True)
        # The frontend reads the id from a data-* attribute, i.e. a string.
        self.assertEqual(self.toggle(str(img.id), "select").json()["status"],
                         "success")
        resp = self.client.delete(
            reverse("delete_image_from_selection", args=[img.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.client.session["selected_images"], [])

    def test_delete_works_when_toggle_sent_a_numeric_id(self):
        img = create_image(with_thumbnail=True)
        self.toggle(img.id, "select")  # numeric image_id in the payload
        resp = self.client.delete(
            reverse("delete_image_from_selection", args=[img.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.client.session["selected_images"], [])


class SelectionViewTests(MediaTestCase):
    def select_in_session(self, *images):
        session = self.client.session
        session["selected_images"] = [str(img.id) for img in images]
        session.save()

    def test_get_empty_selection_renders_template(self):
        resp = self.client.get(reverse("selection"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "images/selection.html")

    def test_get_lists_selected_notes(self):
        a = create_image(note="Premiere", identifier="a", with_thumbnail=True)
        b = create_image(note="Deuxieme", identifier="b", with_thumbnail=True)
        self.select_in_session(a, b)
        resp = self.client.get(reverse("selection"))
        self.assertContains(resp, "Premiere")
        self.assertContains(resp, "Deuxieme")

    def test_delete_one_keeps_the_rest(self):
        a = create_image(identifier="a", with_thumbnail=True)
        b = create_image(identifier="b", with_thumbnail=True)
        self.select_in_session(a, b)
        resp = self.client.delete(
            reverse("delete_image_from_selection", args=[a.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"")
        self.assertEqual(self.client.session["selected_images"], [str(b.id)])

    def test_delete_last_returns_no_images_message(self):
        a = create_image(identifier="a", with_thumbnail=True)
        self.select_in_session(a)
        resp = self.client.delete(
            reverse("delete_image_from_selection", args=[a.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "no-images-message")

    def test_delete_absent_id_returns_400(self):
        a = create_image(identifier="a")
        resp = self.client.delete(
            reverse("delete_image_from_selection", args=[a.id]))
        self.assertEqual(resp.status_code, 400)


class ClearSelectionViewTests(MediaTestCase):
    def select_in_session(self, *images):
        session = self.client.session
        session["selected_images"] = [str(img.id) for img in images]
        session.save()

    def test_clear_empties_session_and_returns_no_images_message(self):
        a = create_image(identifier="a", with_thumbnail=True)
        b = create_image(identifier="b", with_thumbnail=True)
        self.select_in_session(a, b)

        resp = self.client.delete(reverse("clear_selection"))

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "no-images-message")
        self.assertEqual(self.client.session["selected_images"], [])

    def test_clear_when_already_empty_is_a_no_op_success(self):
        resp = self.client.delete(reverse("clear_selection"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.client.session["selected_images"], [])

    def test_get_is_not_allowed(self):
        a = create_image(identifier="a", with_thumbnail=True)
        self.select_in_session(a)
        resp = self.client.get(reverse("clear_selection"))
        self.assertEqual(resp.status_code, 405)
        self.assertEqual(self.client.session["selected_images"], [str(a.id)])


class DownloadTests(MediaTestCase):
    def zip_names(self, response):
        return zipfile.ZipFile(io.BytesIO(response.content)).namelist()

    def test_download_zip_for_single_image(self):
        img = create_image(identifier="solo", with_thumbnail=True)
        resp = self.client.get(reverse("download_zip", args=[img.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/zip")
        self.assertIn("solo.zip", resp["Content-Disposition"])
        names = self.zip_names(resp)
        self.assertIn(os.path.basename(img.file.path), names)
        self.assertIn(os.path.basename(img.thumbnail.path), names)

    def test_download_zip_unknown_id_is_404(self):
        self.assertEqual(
            self.client.get(reverse("download_zip", args=[999999])).status_code, 404)

    def test_download_images_zips_current_selection(self):
        a = create_image(identifier="a", with_thumbnail=True)
        b = create_image(identifier="b")
        session = self.client.session
        session["selected_images"] = [a.id, b.id]
        session.save()
        resp = self.client.get(reverse("download_images"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/zip")
        names = self.zip_names(resp)
        self.assertIn(os.path.basename(a.file.path), names)
        self.assertIn(os.path.basename(a.thumbnail.path), names)
        self.assertIn(os.path.basename(b.file.path), names)

    def test_download_images_empty_selection_is_empty_zip(self):
        resp = self.client.get(reverse("download_images"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.zip_names(resp), [])

    def test_download_images_skips_files_missing_on_disk(self):
        img = create_image(identifier="ghost")
        os.remove(img.file.path)
        session = self.client.session
        session["selected_images"] = [img.id]
        session.save()
        resp = self.client.get(reverse("download_images"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.zip_names(resp), [])


class NavigationContextTests(MediaTestCase):
    def test_nav_combines_static_items_and_pages(self):
        Page.objects.create(slug="apropos", title="A propos",
                            content="x", pub_date=timezone.now())
        resp = self.client.get(reverse("home"))
        nav = resp.context["navigation_items"]
        urls = {item["url"] for item in nav}
        self.assertIn("/", urls)
        self.assertIn("/selection/", urls)
        self.assertIn("/apropos/", urls)

    def test_nav_items_are_localised_and_mark_active(self):
        resp = self.client.get(reverse("home"))
        nav = resp.context["navigation_items"]
        for item in nav:
            self.assertTrue(item["localized_url"].startswith("/fr/"))
        home_item = next(i for i in nav if i["url"] == "/")
        self.assertTrue(home_item["is_active"])


class ImageAdminPreviewTests(MediaTestCase):
    def setUp(self):
        super().setUp()
        from django.contrib.admin.sites import AdminSite

        from .admin import ImageAdmin
        self.admin = ImageAdmin(Image, AdminSite())

    def test_preview_prefers_thumbnail(self):
        img = create_image(with_thumbnail=True)
        html = self.admin.img_preview(img)
        self.assertIn(img.thumbnail.url, html)

    def test_preview_falls_back_to_file(self):
        img = create_image()
        html = self.admin.img_preview(img)
        self.assertIn(img.file.url, html)


class StripEthnicTypeDescriptorsCommandTests(MediaTestCase):
    def make_note(self, identifier, note_fr, note_en):
        img = create_image(identifier=identifier)
        img.note_fr = note_fr
        img.note_en = note_en
        img.save()
        return img

    def test_command_updates_matching_notes_and_leaves_others(self):
        flagged = self.make_note("flagged", "Homme de type africain assis.",
                                  "African type man sitting.")
        untouched = self.make_note("clean", "Un chat noir.", "A black cat.")

        call_command("strip_ethnic_type_descriptors")

        flagged.refresh_from_db()
        untouched.refresh_from_db()
        self.assertEqual(flagged.note_fr, "Homme assis.")
        self.assertEqual(flagged.note_en, "Man sitting.")
        self.assertEqual(untouched.note_fr, "Un chat noir.")
        self.assertEqual(untouched.note_en, "A black cat.")

    def test_dry_run_does_not_save_changes(self):
        flagged = self.make_note("flagged", "Homme de type africain assis.",
                                  "African type man sitting.")

        call_command("strip_ethnic_type_descriptors", "--dry-run")

        flagged.refresh_from_db()
        self.assertEqual(flagged.note_fr, "Homme de type africain assis.")
        self.assertEqual(flagged.note_en, "African type man sitting.")
