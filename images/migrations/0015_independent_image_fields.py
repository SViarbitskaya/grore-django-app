import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0014_add_embedding_hnsw_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='images/',
                validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['tif', 'tiff'])],
            ),
        ),
        migrations.AlterField(
            model_name='image',
            name='thumbnail',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='thumbs/',
                validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg'])],
            ),
        ),
        migrations.AlterField(
            model_name='image',
            name='zoom',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='zoom/',
                validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg'])],
            ),
        ),
    ]
