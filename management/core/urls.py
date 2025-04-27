from core.api.viewset import *
from django.urls import path

urlpatterns = [
    path("signup/", signupView),
    path("login/", loginView),
    path("customer/detail/", customer_detail),
    path("agent/detail/", agent_detail),
    path("ticket/create/", ticket_create),
]
