import logging
from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from core.automation.rule_runner import RuleEngine
from core.constants import Status
from core.models import Agent, Ticket
from core.dumps import BATCH_SIZE
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
            agent.max_customers -= (
                1  # Todo: remove this from every logic: because it should be constant
            )
            agent.save()

            logger.info(f"Ticket {ticket.ticket_id} assigned to {agent.user.username}")


# need updation


@shared_task(bind=True)
def agent_load_balancing():
    """
    Distrribute the load to less load agent
    """
    with transaction.atomic():
        try:
            ticket = Ticket.objects.select_for_update().filter(status=Status.WAITING)
            for waiting_ticket in ticket:
                agent = (
                    Agent.objects.select_for_update()
                    .filter(is_available=True, current_customers__lt=F("max_customers"))
                    .order_by("current_customers")
                    .first()
                )
                if agent is None:
                    logger.info(f"Agent currently unavailable")
                    break
                waiting_ticket.agent = agent
                waiting_ticket.status = Status.ASSIGNED
                waiting_ticket.save()
                agent.current_customers += 1
                if agent.current_customers >= agent.max_customers:
                    agent.is_available = False
                agent.save()

                logger.info(
                    f"[Assigned] {waiting_ticket.ticket_id} to {agent.user.username} | Load: {agent.current_customers}/{agent.max_customers}"
                )
        except Exception as e:
            logger.exception(f"Error: {str(e)}")


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


@shared_task(bind=True)
def apply_rules_to_all_tickets(self):
    """
    Celery task to apply RuleEngine to all tickets in the database in batches.
    """
    total_tickets = Ticket.objects.count()
    results = []

    for start in range(0, total_tickets, BATCH_SIZE):
        end = start + BATCH_SIZE
        ticket_batch = Ticket.objects.all()[start:end]

        for ticket in ticket_batch:
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
