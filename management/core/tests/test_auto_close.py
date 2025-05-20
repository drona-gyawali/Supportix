from datetime import timedelta

from core.automation.auto_close import AutoClose
from core.automation.rule_runner import RuleEngine
from core.models import Agent, Customer, Department, Status, Ticket, User
from django.test import TestCase
from django.utils import timezone


class AutoCloseRuleTestCase(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Support")

        # Create user with agent role
        self.agent_user = User.objects.create_user(
            username="testagent",
            email="testagent@example.com",
            password="testpassword123",
            role="agent",
        )
        self.agent = Agent.objects.create(
            user=self.agent_user,
            department=self.department,
            is_available=True,
            max_customers=5,
            current_customers=0,
        )

        # Create user with customer role
        self.customer_user = User.objects.create_user(
            username="testcustomer",
            email="testcustomer@example.com",
            password="testpassword123",
            role="customer",
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            is_paid=True,
        )

        # Create ticket normally
        self.ticket = Ticket.objects.create(
            ticket_id="TID-TEST123",
            customer=self.customer,
            agent=self.agent,
            issue_title="Test issue for autoclose",
            issue_desc="Description",
            status=Status.WAITING,
        )
        Ticket.objects.filter(pk=self.ticket.pk).update(
            updated_at=timezone.now() - timedelta(days=2)
        )
        self.ticket.refresh_from_db()

    def test_autoclose_rule_escalates_ticket(self):
        rule = AutoClose(ticket_id=self.ticket.ticket_id, inactive_days=1)

        self.assertTrue(rule.should_apply())

        result = rule.apply()

        self.ticket.refresh_from_db()

        self.assertEqual(self.ticket.status, Status.CLOSED)

        self.assertEqual(result["status"], "success")
        self.assertIn("escalated", result["details"].lower())
