from django.test import TestCase
from core.models import Department, User, Agent, Customer, Ticket, Status
from core.automation.rule_runner import RuleEngine
from unittest.mock import patch, MagicMock


class RuleEngineTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Support")

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
            ticket_id="TID-TEST123",
            customer=self.customer,
            agent=self.agent,
            issue_title="Auto-close test",
            issue_desc="Desc",
            status=Status.WAITING,
        )

    @patch("core.automation.rule_runner.AutoClose")
    @patch("core.automation.rule_runner.TagByContent")
    @patch("core.automation.rule_runner.Department_merge")
    def test_rule_engine_run_applies_applicable_rules(
        self, MockDeptMerge, MockTagByContent, MockAutoClose
    ):
        # Configure mocks
        mock_auto = MagicMock()
        mock_auto.should_apply.return_value = True
        mock_auto.apply.return_value = "AutoClosed"
        mock_auto.__class__.__name__ = "AutoClose"
        MockAutoClose.return_value = mock_auto

        mock_tag = MagicMock()
        mock_tag.should_apply.return_value = True
        mock_tag.apply.return_value = "Ai-WrittenTag"
        mock_tag.__class__.__name__ = "TagByContent"
        MockTagByContent.return_value = mock_tag

        mock_merge = MagicMock()
        mock_merge.should_apply.return_value = True
        mock_merge.apply.return_value = "Merged"
        mock_merge.__class__.__name__ = "Department_merge"
        MockDeptMerge.return_value = mock_merge

        engine = RuleEngine(self.ticket.id)
        result = engine.run()

        self.assertEqual(len(result), 3)
        self.assertIn({"rule": "AutoClose", "details": "AutoClosed"}, result)
        self.assertIn({"rule": "Department_merge", "details": "Merged"}, result)
        self.assertIn({"rule": "TagByContent", "details": "Ai-WrittenTag"}, result)
