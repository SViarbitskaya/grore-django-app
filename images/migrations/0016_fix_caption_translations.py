"""Apply the 2026-10 caption translation audit (approved by Philippe
Mairesse) to existing rows, so it reaches Demarchic and production through
the normal deploy (`make up` runs migrate) instead of a manual command run.

clean_caption_pair() also re-runs the September ethnicity cleanups first, so
the result is the same whether or not a server already ran them. It's
idempotent and skips hand-edited captions, so re-running is harmless.

Historical models don't go through Image.save(), so the embeddings of every
changed note are recomputed here (batched). If that fails, the whole
migration rolls back: no caption changes without its matching embedding.
"""

from django.db import migrations


def fix_captions(apps, schema_editor):
    from images.text_cleaning import clean_caption_pair

    Image = apps.get_model("images", "Image")
    changed, en_changed, fr_changed = [], [], []

    for image in Image.objects.order_by("pk").only("identifier", "note", "note_fr", "note_en"):
        new_fr, new_en = clean_caption_pair(image.identifier, image.note_fr, image.note_en)
        if (new_fr, new_en) == (image.note_fr, image.note_en):
            continue
        # The untranslated `note` column mirrors the default (French) text;
        # keep it in step so the admin list doesn't show the old caption.
        if image.note == image.note_fr:
            image.note = new_fr
        elif image.note == image.note_en:
            image.note = new_en
        if new_fr != image.note_fr:
            fr_changed.append(image)
        if new_en != image.note_en:
            en_changed.append(image)
        image.note_fr, image.note_en = new_fr, new_en
        changed.append(image)

    if not changed:
        return

    from images.embeddings import embed_texts

    for images, field, embedding_field in (
        (en_changed, "note_en", "note_en_embedding"),
        (fr_changed, "note_fr", "note_fr_embedding"),
    ):
        with_text = [image for image in images if getattr(image, field)]
        vectors = embed_texts([getattr(image, field) for image in with_text]) if with_text else []
        for image, vector in zip(with_text, vectors):
            setattr(image, embedding_field, vector)
        for image in images:
            if not getattr(image, field):
                setattr(image, embedding_field, None)

    Image.objects.bulk_update(
        changed,
        ["note", "note_fr", "note_en", "note_fr_embedding", "note_en_embedding"],
        batch_size=200,
    )
    print(f"\n  Fixed {len(changed)} caption(s): {len(fr_changed)} French, {len(en_changed)} English "
          f"(embeddings recomputed).")


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0015_independent_image_fields"),
    ]

    operations = [
        migrations.RunPython(fix_captions, migrations.RunPython.noop),
    ]
