from django.urls import path
from .views import view, create, delete, update, group_update, group_create


urlpatterns = [
    path("view", view),
    path("create", create),
    path("delete/<int:id>", delete),
    path("update/<int:id>", update),
    path("update/group/<str:group_name>", group_update),
    path("create/group", group_create)
]
