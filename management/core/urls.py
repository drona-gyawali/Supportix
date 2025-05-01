from core.api import viewset
from django.urls import path

urlpatterns = [
    path("signup/", viewset.signupView, name="signup"),
    path("login/", viewset.loginView, name="login"),
    path("customer/detail/", viewset.customer_detail, name="customer_detail"),
    path("agent/detail/", viewset.agent_detail, name="agent_detail"),
    path("ticket/create/", viewset.ticket_create, name="ticket_create"),
]
