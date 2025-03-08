from django.urls import path
from .viewset import *

urlpatterns = [
    path("signup/", signupView),
    path("login/", loginView),
    path("customer/detail/", customer_detail),
    path("agent/detail/", agent_detail),
    path('trigger-alert/', trigger_alert),
    path('alert/msg/', handle_alert),
]
