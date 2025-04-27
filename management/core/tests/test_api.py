from datetime import datetime
from unittest.mock import patch

from core.models import Agent, Customer, Department, Ticket
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class TicketCreateViewTestCase(APITestCase):
    def setUp(self):
        # Create test customer user and profile
        self.customer_user = User.objects.create_user(
            username="testcustomer",
            password="testpass123",
            email="customer@test.com",
            role="customer",
        )
        self.customer_profile = Customer.objects.create(user=self.customer_user)
        self.department = Department.objects.create(name="support")
        # Create test agent user and profile
        self.agent_user = User.objects.create_user(
            username="testagent",
            password="testpass123",
            email="agent@test.com",
            role="agent",
        )
        self.agent_profile = Agent.objects.create(
            user=self.agent_user, department=self.department
        )

        # Common test data
        self.valid_data = {
            "issue_title": "Login Issue",
            "issue_desc": "Cant login with valid credentials",
            "tags": "authentication",
        }
        self.url = "/app/ticket/create/"

    def test_unauthenticated_access(self):
        """Unauthenticated users should get 403 Forbidden"""
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_agent_cannot_create_ticket(self):
        """Agents should not be able to create tickets"""
        self.client.force_authenticate(user=self.agent_user)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)

    def test_customer_create_ticket_success(self):
        """Authenticated customers should create tickets successfully"""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 1)
        self.assertIn("success", response.data)

        ticket = Ticket.objects.first()
        self.assertEqual(ticket.customer, self.customer_profile)
        self.assertEqual(ticket.issue_title, self.valid_data["issue_title"])

    # def test_ticket_id_generation_format(self):
    #     """Ticket IDs should follow the correct format"""
    #     self.client.force_authenticate(user=self.customer_user)

    #     # Mock datetime to control the date part
    #     with patch('core.views.datetime') as mock_datetime:
    #         test_date = datetime.now().strftime("%Y%m")
    #         mock_datetime.now.return_value = test_date

    #         # First ticket
    #         response = self.client.post(self.url, self.valid_data)
    #         ticket1 = Ticket.objects.first()
    #         expected_id1 = 'TES20250401'  # TES from 'testcustomer'
    #         self.assertEqual(ticket1.ticket_id, expected_id1)

    #         # Second ticket
    #         response = self.client.post(self.url, self.valid_data)
    #         ticket2 = Ticket.objects.last()
    #         expected_id2 = 'TES20250401'
    #         self.assertEqual(ticket2.ticket_id, expected_id2)

    def test_invalid_data_submission(self):
        """Invalid data should return 400 Bad Request"""
        self.client.force_authenticate(user=self.customer_user)
        invalid_data = {"issue_title": ""}  # Missing required fields

        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("issue_title", response.data)
        self.assertIn("issue_desc", response.data)

    def test_missing_customer_profile(self):
        """Users without customer profile should get 404"""
        new_user = User.objects.create_user(
            username="nocustomer", password="testpass123"
        )
        self.client.force_authenticate(user=new_user)

        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
