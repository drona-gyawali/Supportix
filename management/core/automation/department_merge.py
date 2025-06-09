""" "
Module: department_merge
This module provides automation for balancing workload across departments by merging underutilized departments with overloaded ones.
It identifies departments with low and high ticket loads and reassigns tickets from overloaded departments to underutilized ones,
ensuring fair distribution of work among agents.
Classes:
    Department_merge:
        - Inherits from BaseRule.
        - Determines if merging is needed based on ticket load thresholds.
        - Reassigns tickets from overloaded to underutilized departments.
Key Concepts:
    - Load distribution among departments.
    - Automated ticket reassignment for fair workload.
    - Utilizes configurable overload and underutilization thresholds.

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""

from core.models import Ticket, Department, Agent
from core.automation.base_rule import BaseRule
from core.constants import Status
from django.db import models
from core.dumps import OVERLOAD_THRESHOLD, UNDERUTILIZED_THRESHOLD
import logging

logger = logging.getLogger(__name__)


class Department_merge(BaseRule):
    """
    Rule to automatically merged the underutilized department to high load department
    """

    def __init__(self, ticket, **kwargs):
        super().__init__(ticket, **kwargs)

    def should_apply(self):
        try:
            loads = (
                Ticket.objects.filter(status=Status.WAITING, agent__isnull=False)
                .values("agent__department_id")
                .annotate(count=models.Count("id"))
            )
        except Exception as e:
            logger.error("Error Occured", str(e))

        load_map = {items["agent__department_id"]: items["count"] for items in loads}
        for dept in Department.objects.all():
            load_map.setdefault(dept.id, 0)

        max_load = max(load_map.values())
        min_load = min(load_map.values())

        return max_load > OVERLOAD_THRESHOLD and min_load < UNDERUTILIZED_THRESHOLD

    def apply(self):

        loads = (
            Ticket.objects.filter(status=Status.WAITING, agent__isnull=False)
            .values("agent__department_id")
            .annotate(count=models.Count("id"))
        )

        load_map = {item["agent__department_id"]: item["count"] for item in loads}
        for dept in Department.objects.all():
            load_map.setdefault(dept.id, 0)

        overload_dept_id = max(load_map, key=load_map.get)
        underload_dept_id = min(load_map, key=load_map.get)

        # exact count e.g. 1,2,4
        overloaded_count = load_map[overload_dept_id]
        underloaded_count = load_map[underload_dept_id]

        diff = overloaded_count - underloaded_count
        num_to_move = max(1, diff // 2)

        logger.info(
            f"Reassigning {num_to_move} tickets "
            f"from Dept {overload_dept_id} ({overloaded_count}) "
            f"to Dept {underload_dept_id} ({underloaded_count})"
        )

        target_agent = Agent.objects.filter(department_id=underload_dept_id).first()

        tickets_qs = Ticket.objects.filter(
            status=Status.WAITING, agent__department_id=overload_dept_id
        ).order_by("created_at")
        # extract only id not a tuple
        ticket_ids = list(tickets_qs.values_list("id", flat=True)[:num_to_move])

        if not ticket_ids:
            logger.info("No tickets to reassign.")
            return

        updated = Ticket.objects.filter(id__in=ticket_ids).update(agent=target_agent)
        logger.info(f"Successfully reassigned {updated} tickets.")
