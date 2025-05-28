from chat.models import ChatGroup, GroupMessage
from chat.serializers import (
    ChatSerializers,
    FileAttachmentSerializers,
    GroupSerializers,
    ImageAttachmentSerializer,
)
from rest_framework import authentication, generics, permissions, status
from rest_framework.decorators import APIView
from rest_framework.response import Response


class ChatMessageView(generics.ListAPIView):
    """
    API endpoint to retrieve chat groups and their messages.

    Request Method: GET /chat/messages/

    Responses:
    - 200 OK: Returns a list of chat groups and their messages.
    - 401 Unauthorized: Authentication failed.
    """

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


chat_view = ChatMessageView.as_view()


class ChatCreateView(generics.CreateAPIView):
    """
    API endpoint to create a group message.

    Request Method: POST /chat/messages/create

    Responses:
    - 201 Created: Message has been created.
    - 400 Bad Request: Unable to create message.
    - 401 Unauthorized: Authentication failed.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GroupSerializers
    authentication_classes = [authentication.SessionAuthentication]


chat_create = ChatCreateView.as_view()


class ChatDeleteView(generics.DestroyAPIView):
    """
    API endpoint to delete a group message by its ID.

    Request Method: DELETE /chat/messsages/int:id/delete/

    Responses:
    - 200 OK: Message has been deleted.
    - 401 Unauthorized: Authentication failed.
    - 403 Forbidden: User does not have permission to delete the message.
    - 404 Not Found: Message with the specified ID does not exist.
    """

    permission_classes = [permissions.IsAdminUser]
    serializer_class = GroupSerializers
    queryset = GroupMessage.objects.all()
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({"message": "Message has been deleted."})


msg_delete = ChatDeleteView.as_view()


class ChatUpdateView(generics.UpdateAPIView):
    """
    API endpoint to update a group message by its ID.

    Request Method: PUT chat/messages/<int:id>/update/

    Responses:
    - 200 OK: Message has been updated.
    - 400 Bad Request: Unable to update message.
    - 401 Unauthorized: Authentication failed.
    - 404 Not Found: Message with the specified ID does not exist.
    """

    serializer_class = GroupSerializers
    authentication_classes = [authentication.SessionAuthentication]
    queryset = GroupMessage.objects.all()
    lookup_field = "id"


msg_update = ChatUpdateView.as_view()


class GroupNameCreate(generics.CreateAPIView):
    """
    API endpoint to create a new chat group.

    Request Method: POST /chat/groups/create/

    Responses:
    - 201 Created: Chat group created successfully.
    - 400 Bad Request: Invalid data provided.
    - 401 Unauthorized: Authentication credentials were not provided or are invalid.
    """

    serializer_class = ChatSerializers
    queryset = ChatGroup.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


group_create = GroupNameCreate.as_view()


class GroupNameUpdate(generics.UpdateAPIView):
    """
    API endpoint to update the group name of a chat group.

        Request Method: PUT/PATCH /chat/groups/str:<group_name>/update/

        Path Parameters:
        - group_name (str): The current name of the chat group to be updated.

        Request Body:
        - group_name (str): The new name for the chat group.

        Responses:
        - 200 OK: Group name updated successfully.
        - 400 Bad Request: Invalid data provided.
        - 401 Unauthorized: Authentication credentials were not provided or are invalid.
        - 404 Not Found: Chat group with the specified group_name does not exist.
    """

    serializer_class = ChatSerializers
    queryset = ChatGroup.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "group_name"


group_update = GroupNameUpdate.as_view()


class FileAttachment(APIView):
    """
    API endpoint to upload the file such as `.pdf`.

        Request Method: POST /chat/upload_file/

        Responses:
        - 200 OK: File uploaded
        - 400 Bad Request: Unable to upload file.
        - 401 Unauthorized: Authentication failed.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        client = request.user
        if not client:
            return Response(
                {"error": "Unauthorized to upload file "},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = FileAttachmentSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"success": "File uploaded"}, status=status.HTTP_200_OK)
        return Response(
            {"failed": "Unable to upload file", "detail_error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


upload_file = FileAttachment.as_view()


class ImageAttachment(APIView):
    """
    API endpoint to upload the image file.

        Request Method: POST /chat/upload_image/

        Responses:
        - 200 OK:Image uploaded
        - 400 Bad Request: Unable to upload image.
        - 401 Unauthorized: Authentication failed.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        client = request.user
        if not client:
            return Response(
                {"error": "Unauthorized to upload images"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = ImageAttachmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"success": "Image uploaded"}, status=status.HTTP_200_OK)
        return Response(
            {"failed": "Unable to upload image", "detail_error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


upload_image = ImageAttachment.as_view()
