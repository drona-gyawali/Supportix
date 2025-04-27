from django.urls import path

from .views import create, delete, group_create, group_update, update, view

urlpatterns = [
    path("view", view),
    path("create", create),
    path("delete/<int:id>", delete),
    path("update/<int:id>", update),
    path("update/group/<str:group_name>", group_update),
    path("create/group", group_create),
]
