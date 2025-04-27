from core.constants import Role, Status
from core.dumps import CONTEXT_403
from core.models import Agent, Customer, Department, Ticket
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import model_to_dict
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(
            username="customer1",
            email="customer1@example.com",
            password="password123",
            role=Role.CUSTOMER,
        )
        self.agent_user = User.objects.create_user(
            username="agent1",
            email="agent1@example.com",
            password="password123",
            role=Role.AGENT,
        )
        self.admin_user = User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="password123",
            role=Role.ADMIN,
        )

    def test_user_role_methods(self):
        self.assertTrue(self.customer_user.is_customer())
        self.assertFalse(self.customer_user.is_agent())
        self.assertFalse(self.customer_user.is_admin())

        self.assertTrue(self.agent_user.is_agent())
        self.assertFalse(self.agent_user.is_customer())
        self.assertFalse(self.agent_user.is_admin())

        self.assertTrue(self.admin_user.is_admin())
        self.assertFalse(self.admin_user.is_customer())
        self.assertFalse(self.admin_user.is_agent())


class DepartmentModelTest(TestCase):
    def test_department_creation(self):
        department = Department.objects.create(name="IT Support")
        self.assertEqual(str(department), "IT Support")
        self.assertEqual(Department.objects.count(), 1)

    def test_department_unique_name(self):
        Department.objects.create(name="IT Support")
        with self.assertRaises(Exception):  # Django will raise an integrity error
            Department.objects.create(name="IT Support")


class CustomerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer1",
            email="customer1@example.com",
            password="password123",
            role=Role.CUSTOMER,
        )
        self.customer = Customer.objects.create(
            user=self.user, solved_issues=3, is_paid=True
        )

        # Create a non-customer user for testing validation
        self.agent_user = User.objects.create_user(
            username="agent1",
            email="agent1@example.com",
            password="password123",
            role=Role.AGENT,
        )

    def test_customer_creation(self):
        self.assertEqual(str(self.customer), f"Customer: {self.user.username}")
        self.assertEqual(self.customer.solved_issues, 3)
        self.assertTrue(self.customer.is_paid)

    def test_get_details(self):
        details = Customer.get_details("customer1")
        self.assertEqual(details["user"], self.user.id)
        self.assertEqual(details["solved_issues"], 3)
        self.assertTrue(details["is_paid"])

    def test_get_details_not_found(self):
        details = Customer.get_details("nonexistent")
        self.assertEqual(details, {"error": "Customer not found."})

    def test_invalid_role_validation(self):
        with self.assertRaises(ValueError):
            Customer.objects.create(user=self.agent_user)


class AgentModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="IT Support")

        self.agent_user = User.objects.create_user(
            username="agent1",
            email="agent1@example.com",
            password="password123",
            role=Role.AGENT,
        )

        self.agent = Agent.objects.create(
            user=self.agent_user,
            department=self.department,
            current_customers=3,
            max_customers=5,
            is_available=True,
        )

        # Create a non-agent user for testing validation
        self.customer_user = User.objects.create_user(
            username="customer1",
            email="customer1@example.com",
            password="password123",
            role=Role.CUSTOMER,
        )

    def test_agent_creation(self):
        self.assertEqual(
            str(self.agent),
            f"Agent: {self.agent_user.username} ({self.department.name})",
        )
        self.assertEqual(self.agent.current_customers, 3)
        self.assertEqual(self.agent.max_customers, 5)
        self.assertTrue(self.agent.is_available)

    def test_has_capacity(self):
        self.assertTrue(self.agent.has_capacity)

        # Test when at capacity
        self.agent.current_customers = 5
        self.agent.save()
        self.assertFalse(self.agent.has_capacity)

    def test_get_details(self):
        details = Agent.get_details("agent1")
        self.assertEqual(details["id"], self.agent.id)
        self.assertEqual(details["department"], self.department.name)
        self.assertEqual(details["username"], self.agent_user.username)
        self.assertEqual(details["current_customers"], 3)
        self.assertEqual(details["max_customers"], 5)
        self.assertTrue(details["is_available"])

    def test_get_details_invalid_input(self):
        details = Agent.get_details("")
        self.assertEqual(details, [CONTEXT_403])

        details = Agent.get_details(None)
        self.assertEqual(details, [CONTEXT_403])

    def test_get_details_not_found(self):
        details = Agent.get_details("nonexistent")
        self.assertEqual(details, {"error": "Agent not found."})

    def test_invalid_role_validation(self):
        with self.assertRaises(ValueError):
            Agent.objects.create(user=self.customer_user, department=self.department)


class TicketModelTest(TestCase):
    def setUp(self):
        # Create customer
        self.customer_user = User.objects.create_user(
            username="customer1",
            email="customer1@example.com",
            password="password123",
            role=Role.CUSTOMER,
        )
        self.customer = Customer.objects.create(user=self.customer_user)

        # Create agent
        self.department = Department.objects.create(name="IT Support")
        self.agent_user = User.objects.create_user(
            username="agent1",
            email="agent1@example.com",
            password="password123",
            role=Role.AGENT,
        )
        self.agent = Agent.objects.create(
            user=self.agent_user, department=self.department
        )

        # Create ticket
        self.ticket = Ticket.objects.create(
            ticket_id="TID-12345",
            customer=self.customer,
            agent=self.agent,
            issue_title="Login Issue",
            issue_desc="Unable to log in to the platform",
            status=Status.WAITING,
        )

    def test_ticket_creation(self):
        self.assertEqual(str(self.ticket), "TID-12345")
        self.assertEqual(self.ticket.issue_title, "Login Issue")
        self.assertEqual(self.ticket.status, Status.WAITING)

    def test_get_ticket_details(self):
        details = Ticket.get_ticket_details("TID-12345")
        self.assertEqual(details["ticket_id"], "TID-12345")
        self.assertEqual(details["customer"], self.customer.id)
        self.assertEqual(details["agent"], self.agent.id)
        self.assertEqual(details["issue_title"], "Login Issue")
        self.assertEqual(details["issue_desc"], "Unable to log in to the platform")
        self.assertEqual(details["status"], Status.WAITING)

    def test_get_ticket_details_not_found(self):
        details = Ticket.get_ticket_details("nonexistent")
        self.assertEqual(details, {"error": "Ticket not found."})

    def test_ticket_without_agent(self):
        ticket = Ticket.objects.create(
            ticket_id="TID-54321",
            customer=self.customer,
            issue_title="Payment Issue",
            issue_desc="Payment not processed",
            status=Status.WAITING,
        )
        self.assertIsNone(ticket.agent)
        self.assertEqual(str(ticket), "TID-54321")

    def test_ticket_str_without_ticket_id(self):
        # Create ticket without specifying ticket_id
        ticket = Ticket.objects.create(
            customer=self.customer,
            issue_title="Feature Request",
            issue_desc="Need new feature",
            status=Status.WAITING,
        )
        # The __str__ method should use the primary key
        self.assertEqual(str(ticket), f"TID-{ticket.pk}")
