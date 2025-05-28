from chat.models import ChatGroup, FileAttachment, GroupMessage, ImageAttachment
from core.dumps import (
    FileAttachmentSize,
    ImageAttachmentSize,
    FileAttachmentExt,
    ImageAttachmentExt,
)
from rest_framework import serializers


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
    class Meta:
        model = ImageAttachment
        fields = "__all__"
        read_only_fields = ("user",)

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


class FileAttachmentSerializers(serializers.ModelSerializer):
    class Meta:
        model = FileAttachment
        fields = "__all__"
        read_only_fields = ("user",)

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
