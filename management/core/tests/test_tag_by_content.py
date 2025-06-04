from unittest.mock import patch

from django.test import TestCase

from core.automation.tag_by_content import TagByContent
from core.constants import Status
from core.models import Agent, Customer, Department, Ticket, User


class TagByContentTest(TestCase):
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

        self.ticket = Ticket.objects.create(
            ticket_id="TICKET123",
            customer=self.customer,
            agent=self.agent,
            issue_title="Billing issue not resolved",
            issue_desc="I was charged twice this month. Please fix this.",
            tag="",  # no tag to begin with
            status=Status.WAITING,
        )

    @patch("core.automation.tag_by_content.generate_tags")
    def test_should_apply_true_if_no_tags(self, mock_generate_tags):
        rule = TagByContent(ticket=self.ticket.ticket_id)
        self.assertTrue(rule.should_apply())

    @patch("core.automation.tag_by_content.generate_tags")
    def test_should_apply_false_if_tags_exist(self, mock_generate_tags):
        self.ticket.tag = "billing"
        self.ticket.save()
        rule = TagByContent(ticket=self.ticket.ticket_id)
        self.assertFalse(rule.should_apply())

    @patch("core.automation.tag_by_content.generate_tags")
    def test_apply_adds_tags(self, mock_generate_tags):
        mock_generate_tags.return_value = ["billing", "charge"]
        rule = TagByContent(ticket=self.ticket.ticket_id)
        response = rule.apply()

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.tag, "billing, charge")
        self.assertIn("success", response)
        self.assertIn("billing", response["success"])

    @patch("core.automation.tag_by_content.generate_tags")
    def test_apply_skips_if_tags_already_exist(self, mock_generate_tags):
        self.ticket.tag = "support"
        self.ticket.save()

        rule = TagByContent(ticket=self.ticket.ticket_id)
        response = rule.apply()

        self.assertIn("Skipping", response["message"])

    @patch("core.automation.tag_by_content.generate_tags")
    def test_apply_returns_message_if_no_tags_generated(self, mock_generate_tags):
        mock_generate_tags.return_value = []
        rule = TagByContent(ticket=self.ticket.ticket_id)
        response = rule.apply()
        self.assertIn("No tags generated", response["message"])
