"""
Testcases for all API used in core/api/viewsets

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""

import json
from datetime import datetime, timedelta
# import uuid
from decimal import Decimal
from unittest import mock
from unittest.mock import MagicMock, patch

import stripe
from django.db.models import F
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.test import APIClient

from core.constants import Status
from core.models import (Agent, Customer, Department, PaymentDetails, Ticket,
                         User)


@override_settings(STRIPE_SECRET_KEY="sk_test_123", STRIPE_WEBHOOK_SECRET="whsec_test")
class ApiViewsTest(TestCase):
    """Test cases for all API endpoints in a single class."""

    def setUp(self):
        """Set up common test data for all API tests."""

        self.client = APIClient()

        self.signup_url = reverse("signup")
        self.login_url = reverse("token-obtain-pair")
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
        self.customer_detail_url = reverse(
            "customer_detail", kwargs={"pk": self.customer.id}
        )

        self.agent = Agent.objects.create(
            user=self.agent_user,
            is_available=True,
            max_customers=5,
            current_customers=2,
            department=self.department,
        )

        self.agent_detail_url = reverse("agent_detail", kwargs={"pk": self.agent.id})

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

        self.ticket_reopen_url = reverse(
            "ticket_reopen", kwargs={"id": self.ticket.ticket_id}
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
        # API customer/<int:pk>/detail/ : running the query via get_object_or_404(...)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_detail(self):
        """Test agent detail retrieval."""
        self.client.force_authenticate(user=self.agent_user)

        with mock.patch("core.validators.get_user", return_value="testagent"):
            response = self.client.get(self.agent_detail_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_detail_unauthorized(self):
        """Test agent detail retrieval with unauthorized access"""
        response = self.client.get(self.agent_detail_url)
        # API agent/<int:pk>/detail/ : running the query via get_object_or_404(...)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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

    def test_ticket_reopen(self):
        """Test ticket reopen with valid ticket ID."""
        self.ticket.status = Status.CLOSED
        self.ticket.save()

        response = self.client.get(self.ticket_reopen_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("success", response.data)
        self.assertEqual(
            response.data["success"], f"Status changed to {Status.WAITING}"
        )

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Status.WAITING)
        self.assertIsNone(self.ticket.queued_at)

    # Stripe Payment logic are tested on customers only -> because we are trying
    # to use some diff payment gateway for agents and admin.
    @patch("core.api.payments.validators.get_supported_currencies")
    @patch("stripe.PaymentIntent.create")
    def test_create_payment_intent_success(
        self, mock_pi_create, mock_get_supported_currencies
    ):
        mock_get_supported_currencies.return_value = ["USD", "EUR"]
        mock_intent = MagicMock()
        mock_intent.client_secret = "cs_test_123"
        mock_intent.id = "pi_test_456"
        mock_pi_create.return_value = mock_intent

        self.client.force_authenticate(user=self.customer_user)

        url = reverse("stripe_payment")
        data = {"amount": 19.99, "currency": "usd", "description": "test transaction"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("client_secret", response.data)
        self.assertIn("payment_intent_id", response.data)
        self.assertEqual(response.data["client_secret"], "cs_test_123")
        self.assertEqual(response.data["payment_intent_id"], "pi_test_456")
        mock_pi_create.assert_called_once()
        args, kwargs = mock_pi_create.call_args
        self.assertEqual(kwargs["amount"], int(19.99 * 100))
        self.assertEqual(kwargs["currency"], "USD")
        self.assertEqual(kwargs["metadata"]["user_id"], self.customer_user.id)

    @patch("core.validators.get_supported_currencies")
    def test_create_payment_intent_invalid_currency(self, mock_currencies):
        mock_currencies.return_value = ["EUR"]
        url = reverse("stripe_payment")
        data = {"amount": 10, "currency": "USD"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @patch("core.validators.get_supported_currencies")
    def test_create_payment_intent_invalid_amount(self, mock_currencies):
        mock_currencies.return_value = ["USD"]
        url = reverse("stripe_payment")
        data = {"amount": None, "currency": "USD"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @patch("stripe.Webhook.construct_event")
    def test_webhook_payment_succeeded_creates_record(self, mock_construct):
        intent_id = "pi_webhook_123"
        amount_cents = 2500
        fake_intent = {
            "id": intent_id,
            "amount": amount_cents,
            "metadata": {"user_id": str(self.customer_user.id)},
        }
        fake_event = {
            "type": "payment_intent.succeeded",
            "data": {"object": fake_intent},
        }
        mock_construct.return_value = fake_event

        url = reverse("stripe_event")
        payload = json.dumps({"dummy": "data"})
        headers = {"HTTP_STRIPE_SIGNATURE": "testsig"}
        response = self.client.post(
            url, payload, content_type="application/json", **headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment = PaymentDetails.objects.get(stripe_payment_intent_id=intent_id)
        self.assertTrue(payment.payment_verified)
        self.assertEqual(payment.amount, Decimal(amount_cents / 100))
        self.assertEqual(payment.user, self.customer_user)

    @patch(
        "stripe.Webhook.construct_event",
        side_effect=stripe.error.SignatureVerificationError("sig error", "invalidsig"),
    )
    def test_webhook_invalid_signature(self, mock_construct):
        url = reverse("stripe_event")
        payload = json.dumps({"dummy": "data"})
        headers = {"HTTP_STRIPE_SIGNATURE": "invalidsig"}
        response = self.client.post(
            url, payload, content_type="application/json", **headers
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("stripe.Webhook.construct_event")
    def test_webhook_payment_failed_logs(self, mock_construct):
        fake_intent = {"id": "pi_fail_789"}
        fake_event = {
            "type": "payment_intent.payment_failed",
            "data": {"object": fake_intent},
        }
        mock_construct.return_value = fake_event

        url = reverse("stripe_event")
        payload = json.dumps({})
        headers = {"HTTP_STRIPE_SIGNATURE": "testsig"}
        response = self.client.post(
            url, payload, content_type="application/json", **headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            PaymentDetails.objects.filter(
                stripe_payment_intent_id="pi_fail_789"
            ).exists()
        )
