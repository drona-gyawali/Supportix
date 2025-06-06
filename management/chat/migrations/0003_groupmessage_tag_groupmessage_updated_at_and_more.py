# Generated by Django 5.2.1 on 2025-05-25 12:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="groupmessage",
            name="tag",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="groupmessage",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name="groupmessage",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="messages",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="Attachement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("chat_image", models.ImageField(upload_to="chat_image/")),
                ("file_image", models.ImageField(upload_to="attachment/")),
                ("file_name", models.CharField(blank=True, max_length=30)),
                ("link", models.URLField(blank=True)),
                ("reaction", models.CharField(blank=True, max_length=50)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "discussion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachment",
                        to="chat.groupmessage",
                    ),
                ),
            ],
        ),
    ]
