from django.core.management.base import BaseCommand

from images.models import Image
from images.text_cleaning import strip_ethnic_descriptors


class Command(BaseCommand):
    help = (
        "Remove a plain-adjective ethnicity description of a person (e.g. "
        "'Femme africaine', 'Asian woman') from Image notes, leaving "
        "descriptions of places/objects/languages untouched. Follow-up to "
        "strip_ethnic_type_descriptors, per Philippe Mairesse's 2026-09-20 "
        "request. Use --dry-run to preview without saving."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Report what would change without saving anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        changed = 0

        for image in Image.objects.all():
            new_fr = strip_ethnic_descriptors(image.note_fr, "fr")
            new_en = strip_ethnic_descriptors(image.note_en, "en")
            fr_changed = new_fr != image.note_fr
            en_changed = new_en != image.note_en

            if not (fr_changed or en_changed):
                continue

            changed += 1
            if fr_changed:
                self.stdout.write(f"[{image.pk}] fr: {image.note_fr!r} -> {new_fr!r}")
            if en_changed:
                self.stdout.write(f"[{image.pk}] en: {image.note_en!r} -> {new_en!r}")

            if not dry_run:
                image.note_fr = new_fr
                image.note_en = new_en
                image.save(update_fields=["note_fr", "note_en"])

        verb = "Would change" if dry_run else "Changed"
        self.stdout.write(self.style.SUCCESS(f"{verb} {changed} image note(s)."))
