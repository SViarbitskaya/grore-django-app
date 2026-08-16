import pgvector.django.vector
from django.db import migrations


def clear_embeddings(apps, schema_editor):
    Image = apps.get_model('images', 'Image')
    Image.objects.update(note_en_embedding=None, note_fr_embedding=None)


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0012_add_embedding_fields'),
    ]

    operations = [
        # 768-dim vectors can't be cast down to 384 dims in place, so clear
        # them first; re-run `manage.py generate_embeddings` after migrating.
        migrations.RunPython(clear_embeddings, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='image',
            name='note_en_embedding',
            field=pgvector.django.vector.VectorField(blank=True, dimensions=384, null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='note_fr_embedding',
            field=pgvector.django.vector.VectorField(blank=True, dimensions=384, null=True),
        ),
    ]
