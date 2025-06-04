"""
The AutoClose class, which is responsible for automatically closing
inactive tickets after a specified period of inactivity. It extends the BaseRule class
and provides methods to check if the rule should be applied and to apply the rule.

The AutoClose class ensures that tickets in a "WAITING" status for a defined number of
days are closed automatically, helping to manage ticket lifecycles efficiently.

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""

from datetime import timedelta

from django.utils import timezone

from core.automation.base_rule import BaseRule
from core.constants import Status
from core.models import AutoEscalate, Ticket


class AutoClose(BaseRule):
    def __init__(self, ticket_id, **kwargs):
        super().__init__(ticket_id, **kwargs)
        self.inactive_days = kwargs.get("inactive_days", 90)

    def should_apply(self):
        try:
            ticket = Ticket.objects.get(ticket_id=self.ticket_id)
        except Ticket.DoesNotExist:
            return False

        return (
            ticket.status == Status.WAITING
            and ticket.updated_at < timezone.now() - timedelta(days=self.inactive_days)
        )

    def apply(self):
        try:
            ticket = Ticket.objects.get(ticket_id=self.ticket_id)
            if not self.should_apply():
                return {
                    "operation": "apply",
                    "status": "failed",
                    "reason": "condition doesnot meet",
                }
            kwargs = {
                "ticket_id": ticket,
                "new_status": Status.CLOSED,
            }
            if ticket.agent:
                kwargs["new_agent"] = ticket.agent

            result = AutoEscalate.escalate_changes(**kwargs)
            return {
                "operation": "apply",
                "status": "success" if result["success"] else "failed",
                "details": result["message"],
            }
        except Ticket.DoesNotExist:
            return {
                "operation": "apply",
                "status": "failed",
                "reason": "Ticket not found",
            }
        except Exception as e:
            return {"operation": "apply", "status": "failed", "reason": str(e)}
