from django.core.management.base import BaseCommand

from images.embeddings import embed_texts
from images.models import Image


class Command(BaseCommand):
    help = "Generate note_en_embedding/note_fr_embedding for images that are missing them."

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-generate embeddings even for images that already have them.',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=32,
            help='Number of notules to encode per batch (default: 32).',
        )

    def handle(self, *args, **options):
        force = options['force']
        batch_size = options['batch_size']

        for field, embedding_field in (
            ('note_en', 'note_en_embedding'),
            ('note_fr', 'note_fr_embedding'),
        ):
            queryset = Image.objects.exclude(**{field: ''}).exclude(**{f'{field}__isnull': True})
            if not force:
                queryset = queryset.filter(**{f'{embedding_field}__isnull': True})

            images = list(queryset)
            if not images:
                self.stdout.write(f'No images need {embedding_field}.')
                continue

            texts = [getattr(image, field) for image in images]
            self.stdout.write(f'Embedding {len(images)} notules for {field}...')
            embeddings = embed_texts(texts, batch_size=batch_size)

            for image, embedding in zip(images, embeddings):
                setattr(image, embedding_field, embedding)

            Image.objects.bulk_update(images, [embedding_field], batch_size=batch_size)
            self.stdout.write(self.style.SUCCESS(f'Updated {len(images)} images for {embedding_field}.'))
