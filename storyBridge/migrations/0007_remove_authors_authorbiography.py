# Generated by Django 5.0.4 on 2025-04-03 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storyBridge', '0006_rename_ratings_bookshelfs_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authors',
            name='authorBiography',
        ),
    ]
