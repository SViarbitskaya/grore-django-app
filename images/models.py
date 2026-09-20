from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.html import mark_safe
from pgvector.django import VectorField, HnswIndex
from PIL import Image as PILImage
import io
import os

NOTULE_EMBEDDING_DIMENSIONS = 384  # paraphrase-multilingual-MiniLM-L12-v2

# Matches scripts/data/generate_thumbnails.py's parameters, so images added
# individually (e.g. via the admin) get thumbnails consistent with ones
# produced by that bulk script.
THUMBNAIL_SIZE = (600, 600)
ZOOM_JPEG_QUALITY = 90
THUMBNAIL_JPEG_QUALITY = 85

class Image(models.Model):
    identifier = models.CharField(max_length=255)
    slug = models.SlugField(null=True, unique=True)
    note = models.TextField(max_length=255)
    pub_date = models.DateTimeField("date published")
    modif_date = models.DateTimeField("date modified")
    # The three image fields are independent: any one can be uploaded alone.
    # `file` (the archival master) is the only source `zoom`/`thumbnail` can
    # be generated from besides each other -- see save() for the derivation
    # rules -- so it's optional too, not required.
    file = models.ImageField(
        upload_to="images/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['tif', 'tiff'])],
    )
    thumbnail = models.ImageField(
        upload_to="thumbs/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg'])],
    )
    zoom = models.ImageField(
        upload_to="zoom/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg'])],
    )
    high_res = models.BooleanField(default=False)
    ai_gen = models.BooleanField(default=False)
    note_en_embedding = VectorField(dimensions=NOTULE_EMBEDDING_DIMENSIONS, null=True, blank=True)
    note_fr_embedding = VectorField(dimensions=NOTULE_EMBEDDING_DIMENSIONS, null=True, blank=True)

    class Meta:
        indexes = [
            HnswIndex(
                name='image_note_en_embedding_hnsw',
                fields=['note_en_embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
            HnswIndex(
                name='image_note_fr_embedding_hnsw',
                fields=['note_fr_embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
        ]

    def save(self, *args, **kwargs):
        # Recompute an embedding whenever its source text actually changes
        # (or on first creation), so notules are searchable immediately
        # without a separate `generate_embeddings` run. Only re-embeds the
        # language that actually changed, not both, and not other rows.
        # Imported lazily (not at module level) so that loading sentence-
        # transformers/torch only happens on an actual save, not on every
        # manage.py invocation that merely imports this model.
        # Fixture loading (`loaddata`) bypasses this (goes through
        # save_base, not save()) -- still needs `generate_embeddings` run
        # afterward, since embedding thousands of rows one at a time inline
        # would be far slower than that command's batched encoding.
        previous = None
        if self.pk:
            try:
                previous = Image.objects.only('note_en', 'note_fr').get(pk=self.pk)
            except Image.DoesNotExist:
                previous = None

        note_en_changed = previous is None or previous.note_en != self.note_en
        note_fr_changed = previous is None or previous.note_fr != self.note_fr

        # Tracked across both blocks below: if the caller did a partial
        # save (update_fields=[...]), any field we compute here must be
        # added to it too, or the computed value never reaches the DB.
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            update_fields = set(update_fields)

        if note_en_changed or note_fr_changed:
            from .embeddings import embed_text

            if note_en_changed:
                self.note_en_embedding = embed_text(self.note_en) if self.note_en else None
                if update_fields is not None:
                    update_fields.add('note_en_embedding')
            if note_fr_changed:
                self.note_fr_embedding = embed_text(self.note_fr) if self.note_fr else None
                if update_fields is not None:
                    update_fields.add('note_fr_embedding')

        # Derive whichever of zoom/thumbnail is missing from the best
        # available higher-quality source. `file` (the TIFF master)
        # outranks `zoom` (a JPG) as a source; `thumbnail` is never a valid
        # source for anything (too small/lossy already). Never overwrites a
        # field that's already set, even if a better source shows up later.
        #   - file only            -> zoom + thumbnail both generated from file
        #   - thumbnail only       -> nothing (no usable source)
        #   - zoom only            -> thumbnail generated from zoom
        #   - file + thumbnail     -> zoom generated from file
        #   - file + zoom          -> thumbnail generated from file
        if self.file and not self.zoom:
            self._generate_jpeg(self.zoom, self.file, quality=ZOOM_JPEG_QUALITY)
            if update_fields is not None:
                update_fields.add('zoom')

        if not self.thumbnail:
            thumbnail_source = self.file or self.zoom
            if thumbnail_source:
                self._generate_jpeg(
                    self.thumbnail, thumbnail_source, size=THUMBNAIL_SIZE, quality=THUMBNAIL_JPEG_QUALITY
                )
                if update_fields is not None:
                    update_fields.add('thumbnail')

        if update_fields is not None:
            kwargs['update_fields'] = update_fields

        super().save(*args, **kwargs)

    def _generate_jpeg(self, target_field, source_field, quality, size=None):
        source_field.open('rb')
        try:
            img = PILImage.open(source_field)
            img.load()
        finally:
            source_field.seek(0)

        img = img.convert("RGB")
        if size is not None:
            img.thumbnail(size, PILImage.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, "JPEG", quality=quality, optimize=True)

        name = os.path.splitext(os.path.basename(source_field.name))[0] + ".jpg"
        target_field.save(name, ContentFile(buffer.getvalue()), save=False)

    def filename(self):
        return os.path.basename(self.file.name) if self.file else ""

    def thumbnail_preview(self):
        if self.thumbnail:
            return mark_safe(u'<img src="%s" />' % self.thumbnail.url)
        return ""
    
    thumbnail_preview.short_description = 'Thumbnail'

    def get_absolute_url(self):
        return reverse("image", kwargs={"slug": self.slug})