from chat.models import ChatGroup, FileAttachment, GroupMessage, ImageAttachement
from core.dumps import (
    FileAttachemenSize,
    FileAttachementExt,
    ImageAttachemenSize,
    ImageAttachementExt,
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
        model = ImageAttachement
        fields = "__all__"

    def validate_chat_image(self, value):
        if not value.name.lower().endswith(tuple(ImageAttachementExt)):
            raise serializers.ValidationError(
                f"Your file has a {value.name} extension, please use one of {ImageAttachementExt}."
            )
        if value.size > ImageAttachemenSize:
            raise serializers.ValidationError(
                f"Your file size is {value.size} bytes, maximum allowed is 5MB."
            )
        return value


class FileAttachmentSerializers(serializers.ModelSerializer):
    class Meta:
        model = FileAttachment
        fields = "__all__"

    def validate_file_image(self, value):
        if not value.name.lower().endswith(tuple(FileAttachementExt)):
            raise serializers.ValidationError(
                f"Your file has a {value.name} extension, please use `.pdf` only."
            )
        if value.size > FileAttachemenSize:
            raise serializers.ValidationError(
                f"Your file size is {value.size} bytes, maximum allowed is 20MB."
            )
        return value
