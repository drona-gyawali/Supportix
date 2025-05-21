import logging
from datetime import timedelta

from celery import shared_task
from core.automation.rule_runner import RuleEngine
from core.constants import Status
from core.models import Agent, Ticket
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)


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

            logger.info(f"Ticket {ticket.ticket_id} assigned to {agent.user.username}")


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
    logger.info(f"Deleted {deleted_count} completed tickets older than 60 days.")


# Todo: implement the batch processing[!important][Memmory Issue]
@shared_task(bind=True)
def apply_rules_to_all_tickets():
    """
    Celery task to apply RuleEngine to all tickets in the database.
    """
    tickets = Ticket.objects.all()
    results = []

    for ticket in tickets:
        try:
            engine = RuleEngine(ticket.ticket_id)
            result = engine.run()
            results.append({"ticket_id": ticket.ticket_id, "result": result})
            logger.info(f"Rules applied to ticket {ticket.ticket_id}: {result}")
        except Exception as e:
            logger.exception(
                f"Failed to apply rules to ticket {ticket.ticket_id}: {str(e)}"
            )

    return results
