from django.db import models
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

class Attachement(models.Model):
    discussion= models.ForeignKey(GroupMessage, on_delete=models.CASCADE, related_name = 'attachment')
    chat_image = models.ImageField(upload_to="chat_image/")
    file_image = models.ImageField(upload_to='attachment/')
    file_name = models.CharField(max_length=30, blank=True)
    link = models.URLField(blank=True)
    reaction = models.CharField(max_length=50,blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f'{{'
            f'"discussion": "{self.discussion.author.username}", '
            f'"chat_image": "{self.chat_image.url if self.chat_image else ""}", '
            f'"file_image": "{self.file_image.url if self.file_image else ""}", '
            f'"file_name": "{self.file_name}", '
            f'"link": "{self.link}", '
            f'"reaction": "{self.reaction}", '
            f'"uploaded_at": "{self.uploaded_at}", '
            f'"updated_at": "{self.updated_at}"'
            f'}}'
        )