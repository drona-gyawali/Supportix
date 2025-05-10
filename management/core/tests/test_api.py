"""
Testcases for all API used in core/api/viewsets

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""

import json
from datetime import datetime, timedelta
from unittest import mock

from core.constants import Status
from core.models import Agent, Customer, Department, Ticket, User
from django.db.models import F
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.test import APIClient


class ApiViewsTest(TestCase):
    """Test cases for all API endpoints in a single class."""

    def setUp(self):
        """Set up common test data for all API tests."""

        self.client = APIClient()

        self.signup_url = reverse("signup")
        self.login_url = reverse("token-obtain-pair")
        self.customer_detail_url = reverse("customer_detail")
        self.agent_detail_url = reverse("agent_detail")
        self.ticket_create_url = reverse("ticket_create")
        self.logout_url = reverse("logout")
        self.department = Department.objects.create(name="Technical Support")

        self.customer_user = User.objects.create_user(
            username="testcustomer",
            email="testcustomer@example.com",
            password="testpassword123",
            role="customer",
        )

        self.agent_user = User.objects.create_user(
            username="testagent",
            email="testagent@example.com",
            password="testpassword123",
            role="agent",
        )

        self.customer = Customer.objects.create(
            user=self.customer_user,
            is_paid=True,
        )

        self.agent = Agent.objects.create(
            user=self.agent_user,
            is_available=True,
            max_customers=5,
            current_customers=2,
            department=self.department,
        )

        self.ticket = Ticket.objects.create(
            ticket_id="TES202505001",
            customer=self.customer,
            issue_title="Test Issue",
            issue_desc="This is a test issue description",
            status=Status.WAITING,
        )

        self.ticket_assign_url = reverse(
            "ticket_assign", kwargs={"id": self.ticket.ticket_id}
        )

        self.signup_payload = {
            "user": {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpassword123",
            },
            "role": "customer",
        }

        self.login_payload = {"username": "testcustomer", "password": "testpassword123"}

        self.ticket_payload = {
            "issue_title": "New Test Issue",
            "issue_desc": "This is a new test issue description",
            "tags": "test, debug, issue",
        }

    def test_valid_signup(self):
        """Test successful user registration."""
        response = self.client.post(
            self.signup_url,
            data=json.dumps(self.signup_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_invalid_signup(self):
        """Test invalid user registration."""
        invalid_payload = {
            "user": {
                "username": "",
                "email": "invalid@example.com",
                "password": "password123",
            },
            "role": "customer",
        }
        response = self.client.post(
            self.signup_url,
            data=json.dumps(invalid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_login(self):
        """Test successful user login."""
        response = self.client.post(
            self.login_url,
            data=json.dumps(self.login_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_login(self):
        """Test invalid user login."""
        invalid_payload = {"username": "testcustomer", "password": "wrongpassword"}
        response = self.client.post(
            self.login_url,
            data=json.dumps(invalid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout(self):
        login_resp = self.client.post(
            self.login_url,
            data=json.dumps(self.login_payload),
            content_type="application/json",
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        access = login_resp.data["access"]
        refresh = login_resp.data["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        logout_resp = self.client.post(
            self.logout_url,
            data=json.dumps({"refresh": refresh}),
            content_type="application/json",
        )
        self.assertEqual(logout_resp.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(logout_resp.data["detail"], "Logout successful")

        refresh_resp = self.client.post(
            reverse("token-refresh-pair"),
            data=json.dumps({"refresh": refresh}),
            content_type="application/json",
        )
        self.assertEqual(refresh_resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_detail_authenticated(self):
        """Test customer detail retrieval for authenticated user."""
        self.client.force_authenticate(user=self.customer_user)

        with mock.patch("core.validators.get_user", return_value="testcustomer"):
            response = self.client.get(self.customer_detail_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_detail_unauthenticated(self):
        """Test customer detail retrieval for unauthenticated user."""
        response = self.client.get(self.customer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_agent_detail(self):
        """Test agent detail retrieval."""
        self.client.force_authenticate(user=self.agent_user)

        with mock.patch("core.validators.get_user", return_value="testagent"):
            response = self.client.get(self.agent_detail_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_detail_unauthorized(self):
        """Test agent detail retrieval with unauthorized role."""
        self.client.force_authenticate(user=self.agent_user)

        with mock.patch("core.validators.get_user", return_value=None):
            response = self.client.get(self.agent_detail_url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ticket_creation_by_customer(self):
        """Test ticket creation by a customer."""
        self.client.force_authenticate(user=self.customer_user)

        with mock.patch(
            "core.validators.get_user", return_value="testcustomer"
        ), mock.patch(
            "django.utils.timezone.now", return_value=make_aware(datetime(2025, 5, 6))
        ):

            response = self.client.post(
                self.ticket_create_url,
                data=json.dumps(self.ticket_payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_ticket_creation_by_agent(self):
        """Test ticket creation by an agent (should fail)."""
        self.client.force_authenticate(user=self.agent_user)

        with mock.patch("core.validators.get_user", return_value=None):
            response = self.client.post(
                self.ticket_create_url,
                data=json.dumps(self.ticket_payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ticket_assignment_with_available_agent(self):
        """Test ticket assignment when an agent is available."""
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.ticket_assign_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Status.ASSIGNED)
        self.assertEqual(self.ticket.agent, self.agent)

        self.agent.refresh_from_db()
        self.assertEqual(self.agent.current_customers, 3)
        self.assertEqual(self.agent.max_customers, 4)

    def test_ticket_fallback_to_queue_and_position(self):
        """When no agent is available, ticket should go into WAITING with correct queue_position and HTTP 202."""

        Agent.objects.update(is_available=False, current_customers=F("max_customers"))

        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.ticket_assign_url)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Status.WAITING)

        self.assertIn("queue_position", response.data)
        self.assertEqual(response.data["queue_position"], 1)

        self.assertIsNotNone(self.ticket.queued_at)

    def test_multiple_tickets_queue_positions(self):
        """
        When two tickets are in the queue (no agents available),the second ticket should report queue_position = 2.
        """
        Agent.objects.update(is_available=False, current_customers=F("max_customers"))

        self.client.force_authenticate(user=self.customer_user)
        first_response = self.client.get(self.ticket_assign_url)
        self.assertEqual(first_response.status_code, status.HTTP_202_ACCEPTED)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Status.WAITING)
        self.assertIsNotNone(self.ticket.queued_at)

        second_ticket = Ticket.objects.create(
            ticket_id="SECOND123",
            customer=self.ticket.customer,
            status=Status.WAITING,
            created_at=self.ticket.created_at + timedelta(seconds=1),
        )

        second_url = reverse("ticket_assign", kwargs={"id": second_ticket.ticket_id})
        second_response = self.client.get(second_url)

        self.assertEqual(second_response.status_code, status.HTTP_202_ACCEPTED)

        second_ticket.refresh_from_db()
        self.assertEqual(second_ticket.status, Status.WAITING)
        self.assertIsNotNone(second_ticket.queued_at)

        self.assertIn("queue_position", second_response.data)
        self.assertEqual(second_response.data["queue_position"], 2)

    def test_ticket_assignment_invalid_ticket_id(self):
        """Test ticket assignment with invalid ticket ID."""
        self.client.force_authenticate(user=self.customer_user)

        invalid_url = reverse("ticket_assign", kwargs={"id": "INVALID001"})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
