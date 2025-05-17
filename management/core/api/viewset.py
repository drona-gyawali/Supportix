"""
This file contains API viewsets for handling user authentication,
user registration, and retrieving details for customers, agents,
and ticket assignments in the support system.

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""

import datetime
import logging
from datetime import datetime

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import now
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from core import dumps, validators
from core.constants import Status
from core.models import Agent, Customer, Ticket
from core.permissions import CanEditOwnOrAdmin
from core.serializer import RegisterSerializer, TicketCreateSerializer
from core.tasks import process_ticket_queue

logger = logging.getLogger(__name__)


class signupView(APIView):
    """
     API endpoint for user signup.

    This endpoint allows a new user to register by providing
    their username, email, password, and role.

    Request Method:
    ```
        POST
    ```

    Request URL:
    ```
        /app/signup/
    ```

    Example Request Body:
        ```
        {
            "user": {
                "username": "dummy_user",
                "email": "dummy_user@example.com",
                "password": "dummy_password"
            },
            "role": "agent"
        }
        ```
    """

    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(dumps.SUCESS_SIGNUP, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


signupView = signupView.as_view()


class Logout(APIView):
    """
    API endpoint for user logout.

    This endpoint allows a user to log out by blacklisting their
    refresh token.

    Request Method:
    ```
        POST
    ```

    Request URL:
    ```
        /api/logout/
    ```

    Example Request Body:
        ```
        {
            "refresh": "your_refresh_token"
        }
        ```

    Responses:
    - 205 Reset Content: Logout successful.
    - 400 Bad Request: Missing or invalid refresh token.
    """

    def post(self, request, format=None):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as exc:
            logger.error("Error during logout: %s", exc, exc_info=True)
            return Response(
                {"detail": "An error occurred during logout. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )


logout = Logout.as_view()


class CustomerDetailView(APIView):
    """
    API endpoint for extracting customer related data.

    Request Method: GET

    URL: /app/customer/<int:pk>/detail/
    """

    permission_classes = [IsAuthenticated | CanEditOwnOrAdmin]

    def get(self, request, pk, format=None):
        customer = get_object_or_404(Customer, id=pk)
        return Response(
            {
                "id": customer.id,
                "username": customer.user.username,
                "full_name": f"{customer.user.first_name} {customer.user.last_name}".strip(),
                "is_paid": customer.is_paid,
                "raise_issue": customer.solved_issues,
            },
            status=status.HTTP_200_OK,
        )


customer_detail = CustomerDetailView.as_view()


class AgentDetailView(APIView):
    """
    API endpoint for extracting agents related data.

    Request Method: GET

    URL: /app/agent/<int:pk>/detail/
    """

    permission_classes = [IsAuthenticated | CanEditOwnOrAdmin]

    def get(self, request, pk, format=None):
        agent = get_object_or_404(Agent, id=pk)
        return Response(
            {
                "id": agent.id,
                "username": agent.user.username,
                "full_name": f"{agent.user.first_name} {agent.user.last_name}".strip(),
                "department": agent.department.name,
                "is_available": agent.is_available,
                "served_customers": agent.current_customers,
            },
            status=status.HTTP_200_OK,
        )


agent_detail = AgentDetailView.as_view()


class TicketCreateView(APIView):
    """
    API endpoint to create Ticket.

    Request Method: POST
    URL: /app/ticket/create/
    ```
    Request Body:
    {
        "issue_title": "your issue title",
        "issue_desc": "your issue desc",
        "tags" : "your issue tags "
    }
    ```
    Note: Only customers are allowed to create Tickets
    """

    def post(self, request, format=None):
        user_username = validators.get_user(request, role="customer")
        if not user_username:
            return Response(
                {"error": "Only customers can create tickets."},
                status=status.HTTP_403_FORBIDDEN,
            )

        customer = Customer.objects.filter(user__username=user_username).first()
        if not customer:
            return Response(
                {"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND
            )
        # Todo: Make more robust
        date_part = now().strftime("%Y%m")
        count = Ticket.objects.filter(created_at__year=datetime.now().year).count() + 1
        ticket_id = f"{user_username[:3].upper()}{date_part}{count:02d}"

        serializer = TicketCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer, ticket_id=ticket_id)
            return Response(
                {"Ticket Id": f"{ticket_id}"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


ticket_create = TicketCreateView.as_view()


class TicketAssignview(APIView):
    """
    API endpoint to assign a ticket to an available agent.

    Request Method: GET
    URL: /app/ticket/<id>/assign/

    Path Parameter:
    - id: Ticket ID to be assigned.

    Responses:
    - 200 OK:
        - Ticket successfully assigned to an agent.
        - If the ticket is already assigned, returns the current assignment details.
    - 202 Accepted:
        - Ticket is queued due to no available agents. Returns the queue position.
    - 400 Bad Request: Invalid ticket ID or no available agent.
    - 404 Not Found: Ticket with the given ID does not exist.
    """

    def get(self, request, id, format=None):
        with transaction.atomic():
            ticket = Ticket.objects.select_for_update().filter(ticket_id=id).first()
            agent = (
                Agent.objects.select_for_update()
                .filter(is_available=True, max_customers__gt=0)
                .first()
            )

            if not ticket:
                return Response(
                    {"Error": "Invalid ticket id"}, status=status.HTTP_404_NOT_FOUND
                )

            if ticket.status == Status.ASSIGNED:
                return Response(
                    {
                        "ticket_id": f"{id}",
                        "customer": f"{ticket.customer.user.username}",
                        "is_paid": f"{ticket.customer.is_paid}",
                        "agent": f"{ticket.agent.user.username}",
                        "status": f"{ticket.status}",
                    },
                    status=status.HTTP_200_OK,
                )

            if agent and agent.has_capacity:
                ticket.agent = agent
                ticket.status = Status.ASSIGNED
                ticket.save()

                agent.max_customers -= 1
                agent.current_customers += 1
                agent.save()

                return Response(
                    {
                        "ticket_id": f"{id}",
                        "customer": f"{ticket.customer.user.username}",
                        "is_paid": f"{ticket.customer.is_paid}",
                        "agent": f"{ticket.agent.user.username}",
                        "status": f"{ticket.status}",
                    },
                    status=status.HTTP_200_OK,
                )
            if ticket.queued_at is None:
                ticket.status = Status.WAITING
                ticket.queued_at = timezone.now()
                ticket.save()
                process_ticket_queue.delay()
            else:
                ticket.status = Status.WAITING
                ticket.save()

            position = (
                Ticket.objects.filter(
                    status=Status.WAITING, created_at__lt=ticket.created_at
                ).count()
            ) + 1

            return Response(
                {
                    "ticket_id": id,
                    "customer": ticket.customer.user.username,
                    "is_paid": ticket.customer.is_paid,
                    "agent": ticket.agent.user.username if ticket.agent else None,
                    "status": ticket.status,
                    "queue_position": position,
                },
                status=status.HTTP_202_ACCEPTED,
            )


ticket_assign = TicketAssignview.as_view()
