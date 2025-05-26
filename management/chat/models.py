from core.models import User
from django.db import models


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


class ImageAttachement(models.Model):
    messages_chat_file = models.ForeignKey(
        GroupMessage, on_delete=models.CASCADE, related_name="chat_attachment"
    )
    chat_image = models.ImageField(upload_to="image/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.messages_chat_file.author.username} uploaded an image"


class FileAttachment(models.Model):
    message_file = models.ForeignKey(
        GroupMessage, on_delete=models.CASCADE, related_name="file_attachment"
    )
    file_image = models.FileField(upload_to="file/")
    file_name = models.CharField(max_length=30, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.message_file.author.username} uploaded {self.file_name}"
