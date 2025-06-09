from rest_framework import serializers

from chat.models import ChatGroup, FileAttachment, GroupMessage, ImageAttachment
from core.dumps import (
    FileAttachmentExt,
    FileAttachmentSize,
    ImageAttachmentExt,
    ImageAttachmentSize,
)


class GroupSerializers(serializers.ModelSerializer):

    replies = serializers.SerializerMethodField()

    class Meta:
        model = GroupMessage
        fields = [
            "id",
            "body",
            "created",
            "group",
            "author",
            "parent",
            "replies",
            "tag",
            "updated_at",
        ]

    def get_replies(self, obj):
        replies = obj.replies.all()
        return GroupSerializers(replies, many=True).data  # recursive seriaizers


class ChatSerializers(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = "__all__"


class ImageAttachmentSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageAttachment
        fields = ["id", "image", "image_url", "updated_at"]
        read_only_fields = ["uploaded_at", "user"]

    def validate_image(self, value):
        if not value.name.lower().endswith(tuple(ImageAttachmentExt)):
            raise serializers.ValidationError(
                f"Your file has a {value.name} extension, please use one of {ImageAttachmentExt}."
            )
        if value.size > ImageAttachmentSize:
            raise serializers.ValidationError(
                f"Your file size is {value.size} bytes, maximum allowed is 5MB."
            )
        return value

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class FileAttachmentSerializers(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = FileAttachment
        fields = ["id", "file", "file_name", "file_url", "updated_at"]
        read_only_fields = ["uploaded_at", "user"]

    def validate_file(self, value):
        if not value.name.lower().endswith(tuple(FileAttachmentExt)):
            raise serializers.ValidationError(
                f"Your file has a {value.name} extension, please use `.pdf` only."
            )
        if value.size > FileAttachmentSize:
            raise serializers.ValidationError(
                f"Your file size is {value.size} bytes, maximum allowed is 20MB."
            )
        return value

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None
