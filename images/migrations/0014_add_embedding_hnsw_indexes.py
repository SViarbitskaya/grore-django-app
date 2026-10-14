from django.db import migrations
from pgvector.django import HnswIndex


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0013_shrink_embedding_dimensions'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='image',
            index=HnswIndex(
                name='image_note_en_embedding_hnsw',
                fields=['note_en_embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
        ),
        migrations.AddIndex(
            model_name='image',
            index=HnswIndex(
                name='image_note_fr_embedding_hnsw',
                fields=['note_fr_embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
        ),
    ]
