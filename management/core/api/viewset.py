"""
This file contains API viewsets for handling user authentication,
user registration, and retrieving details for customers, agents,
and ticket assignments in the support system.

It includes endpoints for:
- User signup
- User login
- Fetching customer details
- Fetching agent details
- Ticket assignment

Copyright (c) Spportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""

import datetime
import logging
from datetime import datetime

from core import dumps, validators
from core.models import Agent, Customer, Ticket
from core.serializer import RegisterSerializer, TicketCreateSerializer
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response

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


class LoginView(APIView):
    """
    API endpoint for user login.

    Request Method: POST
    URL: /app/login/
    ```
    Request Body:
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```
    Responses:
    - 200 OK: Login successful.
    - 400 Bad Request: Invalid credentials.
    - 405 Method Not Allowed: If request method is not POST.
    """

    # ToDo: Add Token based authentication
    def post(self, request, format=None):
        if request.method == "POST":
            username = request.data.get("username")
            password = request.data.get("password")
            process_login = authenticate(request, username=username, password=password)
            if process_login is not None:
                login(request, process_login)
                return Response({"Login Succuessful"}, status=status.HTTP_200_OK)
            return Response(dumps.CONTEXT_400, status=status.HTTP_400_BAD_REQUEST)
        return Response(dumps.CONTEXT_405, status=status.HTTP_405_METHOD_NOT_ALLOWED)


loginView = LoginView.as_view()


class CustomerDetailView(APIView):
    """
    API endpoint for extracting customer related data.

    Request Method: GET

    URL: /app/customer/detail/
    """

    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(dumps.CONTEXT_403)
        customer_name = validators.get_user(request, role="customer")
        if not customer_name:
            return Response(dumps.CONTEXT_403, status=status.HTTP_403_FORBIDDEN)
        details = Customer.get_details(customer_name)
        return Response(details)


customer_detail = CustomerDetailView.as_view()


class AgentDetailView(APIView):
    """
    API endpoint for extracting agents related data.

    Request Method: GET

    URL: /app/agent/detail/
    """

    def get(self, request, format=None):
        agent_name = validators.get_user(request, role="agent")
        if not agent_name:
            return Response(dumps.CONTEXT_403, status=status.HTTP_403_FORBIDDEN)
        details = Agent.get_details(agent_name)
        return Response(details)


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

        # Generate ticket_id
        date_part = datetime.now().strftime("%Y%m")
        count = Ticket.objects.filter(created_at__year=datetime.now().year).count() + 1
        ticket_id = f"{user_username[:3].upper()}{date_part}{count:02d}"

        serializer = TicketCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer, ticket_id=ticket_id)
            return Response(
                {"success": f"Your ticket {ticket_id} has been initialized."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


ticket_create = TicketCreateView.as_view()
