from cloudinary.models import CloudinaryField
from django.db import models

from core.constants import Reaction
from core.models import User


class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.group_name


class GroupMessage(models.Model):
    group = models.ForeignKey(
        ChatGroup, related_name="chat_messages", on_delete=models.CASCADE
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    body = models.CharField(max_length=300)
    tag = models.CharField(max_length=50, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.author.username}: {self.body}"


class ImageAttachment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_related_image",
        null=True,
        blank=True,
    )
    image = CloudinaryField("image")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} uploaded an image"


class FileAttachment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_related_file",
        blank=True,
        null=True,
    )
    file = CloudinaryField("file")
    file_name = models.CharField(max_length=30, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} uploaded {self.file_name}"


class Reaction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reactions", blank=True, null=True
    )
    reaction = models.CharField(
        max_length=50, choices=Reaction.choices, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "reaction")

    def __str__(self):
        return f"{self.user.username} reacted with {self.reaction}"
