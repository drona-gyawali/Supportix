from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.models import Ticket, Department, Agent, User, Customer
from core.automation.department_merge import Department_merge
from core.constants import Status
from core.dumps import OVERLOAD_THRESHOLD, UNDERUTILIZED_THRESHOLD


class DepartmentMergeRuleTest(TestCase):
    def setUp(self):
        self.dept_high = Department.objects.create(name="Technical")
        self.dept_low = Department.objects.create(name="General")

        self.agent_high_user = User.objects.create_user(
            username="high_agent",
            email="high@example.com",
            password="pass",
            role="agent",
        )
        self.agent_high = Agent.objects.create(
            user=self.agent_high_user,
            department=self.dept_high,
            is_available=True,
            max_customers=100,
            current_customers=0,
        )

        self.agent_low_user = User.objects.create_user(
            username="low_agent",
            email="low@example.com",
            password="pass",
            role="agent",
        )
        self.agent_low = Agent.objects.create(
            user=self.agent_low_user,
            department=self.dept_low,
            is_available=True,
            max_customers=100,
            current_customers=0,
        )

        self.customer_user = User.objects.create_user(
            username="cust",
            email="cust@example.com",
            password="pass",
            role="customer",
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            is_paid=True,
        )

        for i in range(OVERLOAD_THRESHOLD + 2):
            Ticket.objects.create(
                ticket_id=f"TID-TECH-{i}",
                customer=self.customer,
                agent=self.agent_high,
                issue_title="Tech issue",
                issue_desc="Desc",
                status=Status.WAITING,
            )
        for i in range(UNDERUTILIZED_THRESHOLD - 1):
            Ticket.objects.create(
                ticket_id=f"TID-GEN-{i}",
                customer=self.customer,
                agent=self.agent_low,
                issue_title="Gen issue",
                issue_desc="Desc",
                status=Status.WAITING,
            )
        Ticket.objects.all().update(created_at=timezone.now() - timedelta(days=1))

    def test_should_apply_when_loads_imbalanced(self):
        rule = Department_merge(ticket=None)
        self.assertTrue(
            rule.should_apply(),
            "should_apply() must return True when one dept is overloaded and another underutilized",
        )

    def test_apply_moves_half_diff(self):
        rule = Department_merge(ticket=None)

        count_high = Ticket.objects.filter(agent__department=self.dept_high).count()
        count_low = Ticket.objects.filter(agent__department=self.dept_low).count()
        diff = count_high - count_low
        expected_to_move = max(1, diff // 2)

        candidate_qs = Ticket.objects.filter(
            status=Status.WAITING, agent__department=self.dept_high
        ).order_by("created_at")
        ids_to_move = list(candidate_qs.values_list("id", flat=True)[:expected_to_move])

        rule.apply()

        after_high = Ticket.objects.filter(agent__department=self.dept_high).count()
        after_low = Ticket.objects.filter(agent__department=self.dept_low).count()

        self.assertEqual(
            after_high,
            count_high - expected_to_move,
            f"{expected_to_move} tickets should be moved out of Technical",
        )
        self.assertEqual(
            after_low,
            count_low + expected_to_move,
            f"{expected_to_move} tickets should be reassigned into General",
        )

        moved_count = Ticket.objects.filter(
            id__in=ids_to_move, agent=self.agent_low
        ).count()
        self.assertEqual(
            moved_count,
            expected_to_move,
            "Reassigned tickets should be assigned to the low-load agent",
        )
