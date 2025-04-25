from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import APIView, api_view
from core.serializer import RegisterSerializer
from core import dumps
from rest_framework import status
from django.contrib.auth import login, authenticate
from rest_framework import generics
from core import validators
from core.models import Agent, Customer, Ticket
import logging
logger = logging.getLogger(__name__)


class signupView(APIView):
    """
     API endpoint for user signup.

    This endpoint allows a new user to register by providing
    their username, email, password, and role.

    **Request Method:**
    ```
        POST
    ```

    **Request URL:**
    ```
        /app/signup/
    ```

    **Example Request Body:**
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

    **Request Method:** POST
    **URL:** /app/login/
    ```
    **Request Body:**
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```
    **Responses:**
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

    **Request Method:** GET

    **URL:** /app/customer/detail/
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

    **Request Method:** GET

    **URL:** /app/agent/detail/
    """

    def get(self, request, format=None):
        agent_name = validators.get_user(request, role="agent")
        if not agent_name:
            return Response(dumps.CONTEXT_403, status=status.HTTP_403_FORBIDDEN)
        details = Agent.get_details(agent_name)
        print(details)
        return Response(details)


agent_detail = AgentDetailView.as_view()


class TicketAssign(APIView):
    def get(self,request,format=None):
        pass

    # ticket/assign/<ticket:number>
    def post(self,request,format=None):
        ticket_obj = Ticket.objects.get(ticket_id=request.ticket_id)
        checker = Ticket.objects.filter(name=ticket_obj)
        if checker:
            release_agent = Agent.objects.filter()
            # Time constraint occur (todo)