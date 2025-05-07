from datetime import timedelta

from celery import shared_task
from core.constants import Status
from core.models import Agent, Ticket
from django.db import transaction
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
    Delete tickets that have been in COMPLETED status for over 60 days.
    Relies on updated_at timestamp.
    """
    cutoff = timezone.now() - timedelta(days=60)
    with transaction.atomic():
        deleted_count, _ = Ticket.objects.filter(
            status=Status.COMPLETED, updated_at__lte=cutoff
        ).delete()
    print(f"Deleted {deleted_count} completed tickets older than 60 days.")
