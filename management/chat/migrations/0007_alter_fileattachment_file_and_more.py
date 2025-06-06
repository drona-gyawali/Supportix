# Generated by Django 5.2.1 on 2025-06-04 14:37

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0006_remove_fileattachment_message_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fileattachment",
            name="file",
            field=cloudinary.models.CloudinaryField(
                max_length=255, verbose_name="file"
            ),
        ),
        migrations.AlterField(
            model_name="imageattachment",
            name="image",
            field=cloudinary.models.CloudinaryField(
                max_length=255, verbose_name="image"
            ),
        ),
    ]
