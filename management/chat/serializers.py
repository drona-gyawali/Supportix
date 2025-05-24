from chat.models import ChatGroup, GroupMessage
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
