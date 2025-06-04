from django.urls import path

from core.api import payments, viewset

urlpatterns = [
    path("customer/<int:pk>/detail/", viewset.customer_detail, name="customer_detail"),
    path("agent/<int:pk>/detail/", viewset.agent_detail, name="agent_detail"),
    path("ticket/create/", viewset.ticket_create, name="ticket_create"),
    path("ticket/<str:id>/assign", viewset.ticket_assign, name="ticket_assign"),
    path("ticket/<str:id>/reopen", viewset.ticket_reopen, name="ticket_reopen"),
    path("api/stripe/webhooks/", payments.stripe_payment_event, name="stripe_event"),
    path("stripe/payments/intents/", payments.stripe_payment, name="stripe_payment"),
]
