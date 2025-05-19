from datetime import timedelta

from celery import shared_task
from core.automation.state_machine import TicketStateMachine
from core.constants import Status
from core.models import Agent, Ticket
from django.db import transaction
from django.db.models import Q
from django.utils import timezone


@shared_task(bind=True)
def process_ticket_queue(self):
    with transaction.atomic():
        waiting_tickets = (
            Ticket.objects.select_for_update()
            .filter(status=Status.WAITING)
            .order_by("created_at")
        )

        for ticket in waiting_tickets:
            agent = (
                Agent.objects.select_for_update()
                .filter(is_available=True, max_customers__gt=0)
                .first()
            )

            if not agent:
                print(f"No available agents for ticket {ticket.ticket_id}")
                break

            ticket.agent = agent
            ticket.status = Status.ASSIGNED
            ticket.save()

            agent.current_customers += 1
            agent.max_customers -= 1
            agent.save()

            print(f"Ticket {ticket.ticket_id} assigned to {agent.user.username}")


@shared_task(bind=True)
def delete_completed_tickets(self):
    """
    Delete tickets that have been COMPLETED or ClOSED status for over 60 days.
    *Relies on updated_at timestamp.
    """
    cutoff = timezone.now() - timedelta(days=60)
    with transaction.atomic():
        deleted_count, _ = Ticket.objects.filter(
            status=Status.COMPLETED | Q(Status.CLOSED), updated_at__lte=cutoff
        ).delete()
    print(f"Deleted {deleted_count} completed tickets older than 60 days.")


@shared_task(bind=True)
def process_state_changed(ticket_id, new_status):
    with transaction.atomic:
        ticket_id = Ticket.objects.select_for_update.get(ticket_id=ticket_id)
        state_machine = TicketStateMachine(ticket_id)
        return state_machine.transition_to(new_status)
