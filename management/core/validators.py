"""
Info:
 Copyright (c) SupportSystem
 Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>

Functions:
- validate_ticket_creation(customer_id): Validates that a customer has no open tickets before creating a new one.
- check_agent_status(customer_id): Checks if a customer has at least one ticket assigned to an agent.
- get_user(request, role=None): Retrieves the username of an authenticated user with an optional role check.
- get_supported_currencies(): Returns a sorted list of all currencies Stripe can accept.

"""

import stripe
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.cache import cache
from .models import Ticket

User = get_user_model()


def validate_ticket_creation(customer_id):
    """
    Ensure the customer has no open tickets before creating a new one.
    """
    open_tickets = Ticket.objects.filter(
        customer_id=customer_id, status__in=["waiting", "assigned"]
    ).exists()
    if open_tickets:
        raise serializers.ValidationError(
            {
                "customer": "You have unresolved tickets. Complete them before creating new ones."
            }
        )


def check_agent_status(customer_id):
    """
    Return True if the given customer has at least one ticket assigned to an agent.
    """
    return Ticket.objects.filter(customer_id=customer_id, agent__isnull=False).exists()


def get_user(request, role=None):
    """
    Return the username if authenticated and else None.
    """
    user = request.user
    if not user.is_authenticated:
        return None
    if user.role != role:
        return None
    return user.username


# For now we are caching the result for one hour:
# If we grow we can make some changes but for now
# Its make sense.
def get_supported_currencies():
    """
    Returns a sorted list of all currencies Stripe can accept (e.g. ['AUD','CAD','EUR','USD',...]).
    """
    cache_key = "stripe_supported_currencies"
    currencies = cache.get(cache_key)
    if currencies is None:
        specs = stripe.CountrySpec.list().auto_paging_iter()
        currency_set = set()
        for spec in specs:
            currencies.update([c.upper() for c in spec.supported_payment_currencies])
        currencies = sorted(currency_set)
        cache.set(cache_key, currencies, timeout=6000)
    return sorted(currencies)
