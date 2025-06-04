from django.urls import path

from chat.api import viewset

urlpatterns = [
    path("messages/", viewset.chat_view, name="chat-message-list"),
    path("messages/create/", viewset.chat_create, name="chat-message-create"),
    path("messages/<int:id>/delete/", viewset.msg_delete, name="chat-message-delete"),
    path("messages/<int:id>/update/", viewset.msg_update, name="chat-message-update"),
    path("groups/create/", viewset.group_create, name="chat-group-create"),
    path(
        "groups/<str:group_name>/update/",
        viewset.group_update,
        name="chat-group-update",
    ),
    path("upload_file/", viewset.upload_file, name="upload-file"),
    path("upload_image/", viewset.upload_image, name="upload-image"),
]
