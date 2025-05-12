from core.api import viewset
from django.urls import path

urlpatterns = [
    path("customer/<int:pk>/detail/", viewset.customer_detail, name="customer_detail"),
    path("agent/<int:pk>/detail/", viewset.agent_detail, name="agent_detail"),
    path("ticket/create/", viewset.ticket_create, name="ticket_create"),
    path("ticket/<str:id>/assign", viewset.ticket_assign, name="ticket_assign"),
]
