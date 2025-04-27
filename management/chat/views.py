from rest_framework import authentication, generics, permissions, status
from rest_framework.response import Response

from .models import ChatGroup, GroupMessage
from .serializers import ChatSerializers, GroupSerializers


class ChatMessageView(generics.ListAPIView):
    queryset = ChatGroup.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication]
    serializer_class = ChatSerializers

    def list(self, request, *args, **kwargs):
        group_message = GroupMessage.objects.all()
        chat_group = ChatGroup.objects.all()

        chat_group_data = ChatSerializers(chat_group, many=True).data
        chat_message_data = GroupSerializers(group_message, many=True).data

        return Response(
            {"group_name": chat_group_data, "message": chat_message_data},
            status=status.HTTP_200_OK,
        )


view = ChatMessageView.as_view()


class ChatCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GroupSerializers
    authentication_classes = [authentication.SessionAuthentication]


create = ChatCreateView.as_view()


class ChatDeleteView(generics.DestroyAPIView):
    # permission_classes = [permissions.IsAdminUser]
    serializer_class = GroupSerializers
    queryset = GroupMessage.objects.all()
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({"message": "Message has been deleted."})


delete = ChatDeleteView.as_view()


class ChatUpdateView(generics.UpdateAPIView):
    serializer_class = GroupSerializers
    authentication_classes = [authentication.SessionAuthentication]
    lookup_field = "id"


update = ChatUpdateView.as_view()


class GroupNameCreate(generics.CreateAPIView):
    serializer_class = ChatSerializers
    queryset = ChatGroup.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]


group_create = GroupNameCreate.as_view()


class GroupNameUpdate(generics.UpdateAPIView):
    serializer_class = ChatSerializers
    queryset = ChatGroup.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]
    lookup_field = "group_name"


group_update = GroupNameUpdate.as_view()
