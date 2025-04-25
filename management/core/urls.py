from django.urls import path
from core.api.viewset import *

urlpatterns = [
    path("signup/", signupView),
    path("login/", loginView),
    path("customer/detail/", customer_detail),
    path("agent/detail/", agent_detail),
]
