from .viewset import *
from rest_framework import serializers
from .models import *


def validate_ticket_creation(customer_id):
    """Validate to check incomplte tickets"""
    if not Ticket.objects.filter(ticket_customer=customer_id, status="completed"):
        raise serializers.ValidationError(
            {
                "Customer": "You already have unresolved tickets. You can only create new tickets after completing the existing ones"
            }
        )


def check_agent_status(customer_id):

    if Customer.objects.filter(
        ticket_to_customer__name=customer_id, agents__isnull=True
    ):
        return True
    else:
        return False


def get_user(request, role=None):
    """
    Fetch the current_user from session and catogorize according to role.
    """
    if not request.user.is_authenticated:
        return None
    try:
        context_userrole = UserDetails.objects.get(user=request.user)
        context_username = request.user.username
        if context_userrole.role == role:
            return context_username
        return None
    except UserDetails.DoesNotExist:
        return None
