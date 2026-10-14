"""Tests for the images app: model helpers, gallery/HTMX view, search,
the session-based selection cart, zip downloads and navigation."""

import io
import json
import os
import re
import shutil
import tempfile
import zipfile
from unittest import mock

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
from .models import Image, NOTULE_EMBEDDING_DIMENSIONS
from .text_cleaning import (
    CAPTION_CORRECTIONS,
    clean_caption_pair,
    fix_brown_hair_translation,
    fix_film_leader_translation,
    strip_ethnic_descriptors,
    strip_ethnic_type_descriptors,
    strip_skin_colour,
)

# Image.save() computes a real embedding via sentence-transformers on every
# save whenever note text changes, and HomeView.get_queryset() computes one
# per search query - both need network access to download the model and a
# writable HF cache, neither available in CI/sandboxed test runs. Patched
# for the whole module so no test depends on that: a fixed dummy vector is
# fine since these tests never assert on embedding values. Two targets:
# images.models does `from .embeddings import embed_text` *inside* save()
# (a fresh lookup on images.embeddings every call), but images.views does
# it at module level, binding its own name once at import time - patching
# only images.embeddings.embed_text would leave that already-bound name
# untouched.
_embed_text_patchers = []


def setUpModule():
    for target in ("images.embeddings.embed_text", "images.views.embed_text"):
        patcher = mock.patch(target, return_value=[0.0] * NOTULE_EMBEDDING_DIMENSIONS)
        patcher.start()
        _embed_text_patchers.append(patcher)


def tearDownModule():
    for patcher in _embed_text_patchers:
        patcher.stop()
    _embed_text_patchers.clear()


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
        # create_image() always sets `file`, which now auto-derives a
        # thumbnail on save() - so a genuinely thumbnail-less image needs no
        # file/zoom source at all (a bare row, as file/thumbnail/zoom are
        # all optional on this model).
        img = Image(identifier="no-media", slug="no-media",
                    pub_date=timezone.now(), modif_date=timezone.now())
        img.save()
        self.assertEqual(img.thumbnail_preview(), "")

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

    def _placeholder(self):
        return str(ImageSearchForm()["search_query"])

    def test_placeholder_in_english(self):
        with translation.override("en"):
            self.assertIn('placeholder="What are you looking for?"', self._placeholder())

    def test_placeholder_in_french(self):
        # Also guards against the placeholder being translated once at import
        # time (eager gettext) instead of per request.
        with translation.override("fr"):
            self.assertIn('placeholder="Que cherchez-vous ?"', self._placeholder())


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


class StripEthnicDescriptorsTests(TestCase):
    """strip_ethnic_descriptors(): the broader follow-up Philippe asked for
    on 2026-09-20 ('everything that puts people in a specific ethnic
    category'), after strip_ethnic_type_descriptors() above had already
    removed the narrower 'de type X'/'X type' classification wording."""

    def test_strips_fr_adjective_after_person_noun(self):
        self.assertEqual(
            strip_ethnic_descriptors("Femme africaine en boubou.", "fr"),
            "Femme en boubou.")

    def test_strips_en_adjective_before_person_noun(self):
        self.assertEqual(
            strip_ethnic_descriptors("African woman in batik boubou.", "en"),
            "Woman in batik boubou.")

    def test_strips_fr_origin_clause(self):
        self.assertEqual(
            strip_ethnic_descriptors("Homme d’origine maghrébine de face.", "fr"),
            "Homme de face.")

    def test_strips_en_origin_clause(self):
        self.assertEqual(
            strip_ethnic_descriptors("Man of North African origin facing forward.", "en"),
            "Man facing forward.")

    def test_leaves_chinese_restaurant_untouched(self):
        # "chinois" here describes the restaurant, not a person - only the
        # "Femme chinoise" occurrence should go.
        self.assertEqual(
            strip_ethnic_descriptors("Femme chinoise debout dans un restaurant chinois.", "fr"),
            "Femme debout dans un restaurant chinois.")
        self.assertEqual(
            strip_ethnic_descriptors("Chinese woman standing in a Chinese restaurant.", "en"),
            "Woman standing in a Chinese restaurant.")

    def test_leaves_non_person_descriptions_untouched(self):
        # Language/script, vegetation, clothing style - not a person.
        for note in (
            "Urne avec inscriptions en arabe.",
            "Falaises et végétations africaines.",
            "Jambes de femme en robe batik africaine avec un enfant.",
        ):
            self.assertEqual(strip_ethnic_descriptors(note, "fr"), note)

    def test_replaces_standalone_subject_noun_fr(self):
        # Deleting "Asiatiques" outright would leave the sentence with no
        # subject at all.
        self.assertEqual(
            strip_ethnic_descriptors("Asiatiques debout dans un escalier.", "fr"),
            "Personnes debout dans un escalier.")

    def test_replaces_standalone_subject_noun_en(self):
        self.assertEqual(
            strip_ethnic_descriptors("Asians standing on a staircase.", "en"),
            "People standing on a staircase.")

    def test_does_not_misfire_subject_fallback_on_adjective_use(self):
        # Regression test: "African child..." was wrongly matched by an
        # earlier version of the standalone-subject fallback (which didn't
        # require what follows to look like a verb), producing the broken
        # "People child...". child(?:ren)? in _EN_PERSON should catch this
        # via the ordinary adjacency rule before the fallback ever runs.
        self.assertEqual(
            strip_ethnic_descriptors("African child resting on a cushion.", "en"),
            "Child resting on a cushion.")
        self.assertEqual(
            strip_ethnic_descriptors("Little Asian child with a cap.", "en"),
            "Little child with a cap.")

    def test_leaves_unusual_word_order_untouched_rather_than_risk_breaking_it(self):
        # "Asian" here precedes a non-person noun ("bust") before the person
        # noun ("woman") - neither the adjacency rule nor the subject
        # fallback (which requires a following "-ing" word) matches, so
        # this is deliberately left alone rather than produce "People bust
        # woman."
        note = "Asian bust woman. Image with stripes."
        self.assertEqual(strip_ethnic_descriptors(note, "en"), note)

    def test_fixes_capitalized_article_left_stranded_by_removal(self):
        # Regression test: "An Asian woman..." -> "An woman..." was broken
        # (the article-fix regex only handled lowercase "an" mid-sentence).
        self.assertEqual(
            strip_ethnic_descriptors("An Asian woman and her daughter.", "en"),
            "A woman and her daughter.")
        self.assertEqual(
            strip_ethnic_descriptors("An Asian man and woman sitting.", "en"),
            "A man and woman sitting.")

    def test_leaves_unrelated_text_untouched(self):
        note = "Un chat noir sur le toit."
        self.assertEqual(strip_ethnic_descriptors(note, "fr"), note)

    def test_leaves_none_and_empty_string_untouched(self):
        self.assertIsNone(strip_ethnic_descriptors(None, "fr"))
        self.assertEqual(strip_ethnic_descriptors("", "en"), "")


class StripEthnicTypeDescriptorsCreoleTests(TestCase):
    """2026-10 audit: "de type créole" was missed by the September list."""

    def test_strips_fr_de_type_creole(self):
        self.assertEqual(
            strip_ethnic_type_descriptors("Visage de femme brune souriante de type créole. Noir et blanc."),
            "Visage de femme brune souriante. Noir et blanc.",
        )

    def test_strips_en_creole_type(self):
        self.assertEqual(
            strip_ethnic_type_descriptors("Face of smiling brunette Creole type woman. Black and white."),
            "Face of smiling brunette woman. Black and white.",
        )


class FixBrownHairTranslationTests(TestCase):
    """2026-10 audit: "brun" (dark-haired) was translated "brown man", which
    reads as skin colour in English."""

    def test_brun_becomes_dark_haired(self):
        self.assertEqual(
            fix_brown_hair_translation("Petit garçon brun souriant.", "Little smiling brown boy."),
            "Little smiling dark-haired boy.",
        )

    def test_keeps_capital_at_sentence_start(self):
        self.assertEqual(
            fix_brown_hair_translation("Homme brun de face.", "Brown man from the front."),
            "Dark-haired man from the front.",
        )

    def test_handles_young_between_brown_and_person(self):
        self.assertEqual(
            fix_brown_hair_translation("Hommes blonds et bruns.", "Blond and brown men; brown young man."),
            "Blond and dark-haired men; dark-haired young man.",
        )

    def test_chatain_becomes_brown_haired(self):
        self.assertEqual(
            fix_brown_hair_translation("Visage de jeune homme châtain à anorak.",
                                       "Face of a young brown man in an anorak."),
            "Face of a young brown-haired man in an anorak.",
        )

    def test_light_chatain_becomes_light_brown_haired(self):
        self.assertEqual(
            fix_brown_hair_translation("Visage de jeune homme châtain clair.",
                                       "Face of a light brown young man."),
            "Face of a light-brown-haired young man.",
        )

    def test_leaves_brown_objects_and_hair_untouched(self):
        en = "Brown-haired man on a brown sofa with brown eyes."
        self.assertEqual(fix_brown_hair_translation("Homme brun sur un canapé marron.", en), en)

    def test_needs_brun_in_french(self):
        # Without "brun"/"châtain" in the source, "brown" is left alone.
        en = "Brown man."
        self.assertEqual(fix_brown_hair_translation("Homme.", en), en)

    def test_leaves_none_and_empty_untouched(self):
        self.assertIsNone(fix_brown_hair_translation("Homme brun.", None))
        self.assertEqual(fix_brown_hair_translation(None, "Brown man."), "Brown man.")


class StripSkinColourTests(TestCase):
    """2026-10 audit: skin-colour descriptions of people removed in both
    languages, per Philippe Mairesse's approval."""

    def test_strips_fr_peau_clause_and_en_dark_skinned(self):
        self.assertEqual(
            strip_skin_colour("Femme à la peau foncée assise sur une banquette.",
                              "Dark-skinned woman sitting on a bench."),
            ("Femme assise sur une banquette.", "Woman sitting on a bench."),
        )

    def test_strips_clause_without_article_and_before_comma(self):
        self.assertEqual(
            strip_skin_colour("à ses côtés une femme à peau foncée, un gobelet à la main.",
                              "next to him a dark-skinned woman, a cup in her hand."),
            ("à ses côtés une femme, un gobelet à la main.",
             "next to him a woman, a cup in her hand."),
        )

    def test_strips_noire_blanche_after_person_and_black_white_before(self):
        self.assertEqual(
            strip_skin_colour(
                "Femme blanche souriante serrant la main d’une femme noire corpulente.",
                "Smiling white woman shaking hands with a heavyset black woman."),
            ("Femme souriante serrant la main d’une femme corpulente.",
             "Smiling woman shaking hands with a heavyset woman."),
        )

    def test_strips_little_black_girl(self):
        self.assertEqual(
            strip_skin_colour("Petite fille noire de profil.", "Little black girl in profile."),
            ("Petite fille de profil.", "Little girl in profile."),
        )

    def test_leaves_clothing_and_black_and_white_untouched(self):
        fr = "Homme en noir et femme en blanc. Noir et blanc."
        en = "Man in black and woman in white. Black and white."
        self.assertEqual(strip_skin_colour(fr, en), (fr, en))

    def test_strips_fr_et_peau_clause(self):
        self.assertEqual(
            strip_skin_colour("Visage d’homme à moustache et peau foncée. Noir et blanc.",
                              "Face of a man with mustache and dark skin. Black and white."),
            ("Visage d’homme à moustache. Noir et blanc.", "Face of a man with mustache. Black and white."),
        )

    def test_strips_english_only_skin_phrases(self):
        # The translation added skin colour the French doesn't mention.
        for fr, en, expected in [
            ("Visage souriant d’enfant.", "Smiling face of a child with dark skin.",
             "Smiling face of a child."),
            ("Couple enlacé, homme et femme.", "Embracing couple, man and woman, with black skin.",
             "Embracing couple, man and woman."),
            ("Visage d’homme brun à lunettes souriant.",
             "Face of dark-haired man in glasses with dark skin smiling.",
             "Face of dark-haired man in glasses smiling."),
            ("Podium avec mannequin.", "Podium with black-skinned model.", "Podium with model."),
        ]:
            self.assertEqual(strip_skin_colour(fr, en), (fr, expected))

    def test_leaves_animal_skins_untouched(self):
        fr, en = "Femme près d'une peau de zèbre.", "Woman near a zebra skin."
        self.assertEqual(strip_skin_colour(fr, en), (fr, en))

    def test_english_needs_skin_mention_in_french(self):
        # "white man" with no skin colour in the French source is left alone
        # rather than guessed at.
        fr, en = "Homme en chemise.", "White man in a shirt."
        self.assertEqual(strip_skin_colour(fr, en), (fr, en))


class FixFilmLeaderTranslationTests(TestCase):
    def test_primer_becomes_film_leader(self):
        self.assertEqual(
            fix_film_leader_translation("Image avec amorce.", "Image with primer."),
            "Image with film leader.",
        )

    def test_capitalised_primer(self):
        self.assertEqual(
            fix_film_leader_translation("Amorce rayée.", "Primer scratched."),
            "Film leader scratched.",
        )

    def test_drops_uncertainty_mark_in_both_languages(self):
        self.assertEqual(
            clean_caption_pair("zzz", "Vue non identifiée. Amorce\u00a0???", "Unidentified view. Primer???"),
            ("Vue non identifiée. Amorce.", "Unidentified view. Film leader."),
        )
        self.assertEqual(clean_caption_pair("zzz", "Amorce\u00a0?", "Film leader?"),
                         ("Amorce.", "Film leader."))

    def test_needs_amorce_in_french(self):
        self.assertEqual(fix_film_leader_translation("Peinture.", "Primer."), "Primer.")


class CleanCaptionPairTests(TestCase):
    def test_runs_september_cleanups_then_audit_fixes(self):
        fr, en = clean_caption_pair(
            "zzz", "Femme africaine et garçon brun.", "African woman and brown boy.")
        self.assertEqual((fr, en), ("Femme et garçon brun.", "Woman and dark-haired boy."))

    def test_applies_per_image_correction(self):
        self.assertEqual(
            clean_caption_pair("A1111",
                               "Champ de course avec trois cavaliers au passage de la ligne d'arrivée. Noir et blanc.",
                               "Race field with three riders crossing the finish line. Black and white."),
            ("Champ de course avec trois cavaliers au passage de la ligne d'arrivée. Noir et blanc.",
             "Racecourse with three riders crossing the finish line. Black and white."),
        )

    def test_per_image_correction_skipped_if_text_was_edited(self):
        # Hand-edited on the server since the audit: leave it alone.
        self.assertEqual(clean_caption_pair("A1111", "Autre.", "Something else."),
                         ("Autre.", "Something else."))

    def test_is_idempotent(self):
        once = clean_caption_pair("A1287", "Petit garçon brun souriant en polo orange. Image abîmée.",
                                  "Little smiling brown boy in orange polo shirt. Damaged image.")
        self.assertEqual(clean_caption_pair("A1287", *once), once)

    def test_every_correction_targets_text_the_patterns_leave_behind(self):
        # Guards against a correction whose "old" substring can never match
        # because an earlier pattern step already rewrote it.
        for identifier, langs in CAPTION_CORRECTIONS.items():
            for lang, pairs in langs.items():
                for old, new in pairs:
                    self.assertNotEqual(old, new, identifier)


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
        self.assertEqual(len(resp.context["images"]), 10)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(resp.context["page_obj"].has_next())

    def test_load_more_trigger_absent_on_last_page(self):
        # Regression test: the infinite-scroll trigger used to render
        # unconditionally, always requesting page_obj.number + 1 - so on the
        # last page it asked for a page past the end and 404'd once it
        # scrolled into view.
        for i in range(15):
            create_image(identifier=f"last{i}")
        last_page_resp = self.client.get(self.url, {"page": 2}, headers={"hx-request": "true"})
        self.assertNotContains(last_page_resp, "load-more-trigger")

        first_page_resp = self.client.get(self.url, headers={"hx-request": "true"})
        self.assertContains(first_page_resp, "load-more-trigger")

    def _next_page_url(self, resp):
        match = re.search(r'hx-get="([^"]+)"', resp.content.decode())
        return match.group(1).replace("&amp;", "&") if match else None

    def test_infinite_scroll_never_repeats_an_image_while_browsing(self):
        # Regression test: with no search, every page request reshuffled
        # the whole collection and sliced it, so page 2 was an independent
        # random sample - captions repeated on scroll and others were never
        # reached. One shuffle seed now carries through the scroll.
        ids = {create_image(identifier=f"s{i}").pk for i in range(25)}
        seen = []
        resp = self.client.get(self.url, headers={"hx-request": "true"})
        while True:
            seen += [image.pk for image in resp.context["images"]]
            next_url = self._next_page_url(resp)
            if not next_url:
                break
            resp = self.client.get(next_url, headers={"hx-request": "true"})
        self.assertEqual(len(seen), len(set(seen)), "an image was shown twice")
        self.assertEqual(set(seen), ids)

    def test_same_seed_gives_same_order_and_new_visit_reshuffles(self):
        for i in range(30):
            create_image(identifier=f"o{i}")
        first = [i.pk for i in self.client.get(self.url, {"seed": 42}).context["images"]]
        again = [i.pk for i in self.client.get(self.url, {"seed": 42}).context["images"]]
        self.assertEqual(first, again)
        seeds = {self.client.get(self.url).context["shuffle_seed"] for _ in range(5)}
        self.assertGreater(len(seeds), 1)

    def test_invalid_seed_falls_back_to_a_fresh_one(self):
        create_image()
        resp = self.client.get(self.url, {"seed": "not-a-number"})
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.context["shuffle_seed"], int)

    def test_next_page_link_url_encodes_the_search_query(self):
        for i in range(15):
            create_image(identifier=f"q{i}", note="chat chien")
        resp = self.client.get(self.url, {"search_query": "chat chien"}, headers={"hx-request": "true"})
        self.assertIn("search_query=chat%20chien", self._next_page_url(resp))

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

    def test_get_lists_selected_references(self):
        a = create_image(note="Premiere", identifier="ref-a", with_thumbnail=True)
        b = create_image(note="Deuxieme", identifier="ref-b", with_thumbnail=True)
        self.select_in_session(a, b)
        resp = self.client.get(reverse("selection"))
        self.assertContains(resp, "ref-a")
        self.assertContains(resp, "ref-b")

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
        # `file` now auto-derives a real, separate thumbnail file on save(),
        # so removing only `file` from disk leaves that thumbnail behind -
        # remove both to genuinely simulate "nothing left on disk".
        os.remove(img.file.path)
        os.remove(img.thumbnail.path)
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
        # create_image() sets `file`, which now auto-derives a thumbnail on
        # save() - so a real "file but no thumbnail" row (the fallback this
        # test covers) can only happen for data predating that feature.
        # Simulate it by clearing thumbnail via a queryset update, which
        # bypasses save() rather than fighting the auto-derivation.
        Image.objects.filter(pk=img.pk).update(thumbnail="")
        img.refresh_from_db()
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


class StripEthnicDescriptorsCommandTests(MediaTestCase):
    def make_note(self, identifier, note_fr, note_en):
        img = create_image(identifier=identifier)
        img.note_fr = note_fr
        img.note_en = note_en
        img.save()
        return img

    def test_command_updates_matching_notes_and_leaves_others(self):
        flagged = self.make_note("flagged", "Femme africaine en boubou.",
                                  "African woman in boubou.")
        untouched = self.make_note("clean", "Un chat noir.", "A black cat.")

        call_command("strip_ethnic_descriptors")

        flagged.refresh_from_db()
        untouched.refresh_from_db()
        self.assertEqual(flagged.note_fr, "Femme en boubou.")
        self.assertEqual(flagged.note_en, "Woman in boubou.")
        self.assertEqual(untouched.note_fr, "Un chat noir.")
        self.assertEqual(untouched.note_en, "A black cat.")

    def test_dry_run_does_not_save_changes(self):
        flagged = self.make_note("flagged", "Femme africaine en boubou.",
                                  "African woman in boubou.")

        call_command("strip_ethnic_descriptors", "--dry-run")

        flagged.refresh_from_db()
        self.assertEqual(flagged.note_fr, "Femme africaine en boubou.")
        self.assertEqual(flagged.note_en, "African woman in boubou.")


class FixCaptionTranslationsCommandTests(MediaTestCase):
    def make_note(self, identifier, note_fr, note_en):
        img = create_image(identifier=identifier)
        img.note_fr = note_fr
        img.note_en = note_en
        img.save()
        return img

    def test_command_updates_matching_notes_and_leaves_others(self):
        flagged = self.make_note("flagged", "Petit garçon brun souriant.",
                                  "Little smiling brown boy.")
        untouched = self.make_note("clean", "Un chat noir.", "A black cat.")

        call_command("fix_caption_translations")

        flagged.refresh_from_db()
        untouched.refresh_from_db()
        self.assertEqual(flagged.note_fr, "Petit garçon brun souriant.")
        self.assertEqual(flagged.note_en, "Little smiling dark-haired boy.")
        self.assertEqual(untouched.note_en, "A black cat.")

    def test_recomputes_embedding_only_for_the_changed_language(self):
        flagged = self.make_note("flagged", "Petit garçon brun souriant.",
                                  "Little smiling brown boy.")
        with mock.patch("images.embeddings.embed_text",
                        return_value=[1.0] * NOTULE_EMBEDDING_DIMENSIONS) as embed:
            call_command("fix_caption_translations")

        embed.assert_called_once_with("Little smiling dark-haired boy.")
        flagged.refresh_from_db()
        self.assertEqual(list(flagged.note_en_embedding), [1.0] * NOTULE_EMBEDDING_DIMENSIONS)
        self.assertEqual(list(flagged.note_fr_embedding), [0.0] * NOTULE_EMBEDDING_DIMENSIONS)

    def test_dry_run_does_not_save_changes(self):
        flagged = self.make_note("flagged", "Petit garçon brun souriant.",
                                  "Little smiling brown boy.")

        call_command("fix_caption_translations", "--dry-run")

        flagged.refresh_from_db()
        self.assertEqual(flagged.note_en, "Little smiling brown boy.")


class FixCaptionTranslationsMigrationTests(MediaTestCase):
    """Data migration 0016 is what actually applies the audit on deploy."""

    def run_migration(self):
        import importlib
        from django.apps import apps as global_apps
        module = importlib.import_module("images.migrations.0016_fix_caption_translations")
        module.fix_captions(global_apps, None)

    def test_fixes_notes_syncs_base_note_and_reembeds_changed_language_only(self):
        img = create_image(identifier="A1287")
        Image.objects.filter(pk=img.pk).update(
            note="Petit garçon brun souriant.", note_fr="Petit garçon brun souriant.",
            note_en="Little smiling brown boy.",
            note_en_embedding=[0.0] * NOTULE_EMBEDDING_DIMENSIONS,
            note_fr_embedding=[0.0] * NOTULE_EMBEDDING_DIMENSIONS,
        )
        untouched = create_image(identifier="clean")
        Image.objects.filter(pk=untouched.pk).update(note_fr="Un chat noir.", note_en="A black cat.")

        with mock.patch("images.embeddings.embed_texts",
                        side_effect=lambda texts: [[1.0] * NOTULE_EMBEDDING_DIMENSIONS for _ in texts]) as embed:
            self.run_migration()

        embed.assert_called_once_with(["Little smiling dark-haired boy."])
        row = Image.objects.get(pk=img.pk)
        self.assertEqual(row.note_en, "Little smiling dark-haired boy.")
        self.assertEqual(row.note_fr, "Petit garçon brun souriant.")
        self.assertEqual(list(row.note_en_embedding), [1.0] * NOTULE_EMBEDDING_DIMENSIONS)
        self.assertEqual(list(row.note_fr_embedding), [0.0] * NOTULE_EMBEDDING_DIMENSIONS)
        self.assertEqual(Image.objects.get(pk=untouched.pk).note_en, "A black cat.")

    def test_no_changes_does_not_load_the_embedding_model(self):
        create_image(identifier="clean")
        with mock.patch("images.embeddings.embed_texts") as embed:
            self.run_migration()
        embed.assert_not_called()
