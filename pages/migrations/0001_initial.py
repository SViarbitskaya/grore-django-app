# Generated by Django 5.0.1 on 2024-02-22 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=10)),
                ('title_en', models.CharField(max_length=10, null=True)),
                ('title_fr', models.CharField(max_length=10, null=True)),
                ('content', models.TextField(max_length=255)),
                ('content_en', models.TextField(max_length=255, null=True)),
                ('content_fr', models.TextField(max_length=255, null=True)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
    ]