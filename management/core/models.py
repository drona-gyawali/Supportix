"""
Info:
 Copyright (c) SupportSystem
 Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>

This module defines the core models for the Support System application, including custom user roles, 
departments, customers, agents, and tickets. These models are used to manage the application's 
business logic and data relationships.

Classes:
    User(AbstractUser):
        Extends Django's AbstractUser to include a role field and profile picture. 
        Provides methods to check the user's role.

    Department(models.Model):
        Represents a department in the organization. Each department has a unique name.

    Customer(models.Model):
        Represents a customer profile linked to a user with the role 'customer'. 
        Includes fields for solved issues and payment status. Provides methods to 
        retrieve customer details and validate the role during save.

    Agent(models.Model):
        Represents an agent profile linked to a user with the role 'agent'. 
        Includes fields for department, customer capacity, availability, and creation date. 
        Provides methods to retrieve agent details, check capacity, and validate the role during save.

    Ticket(models.Model):
        Represents a support ticket created by a customer. Includes fields for ticket ID, 
        customer, agent, issue details, status, and creation date. Provides methods to 
        retrieve ticket details.

Constants:
    STATUS_CHOICES:
        Defines the possible statuses for a ticket (e.g., waiting, resolved).
    ROLE:
        Defines the possible roles for a user (e.g., customer, agent, admin).
    CONTEXT_403:
        Represents a forbidden context for invalid operations.
"""
from django.db import models
from django.forms import model_to_dict
from django.contrib.auth.models import AbstractUser
from core.dumps import CONTEXT_403
from core.constants import Role,Status
from django.conf import settings

class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        help_text="Defines the user's role: customer, agent, or admin."
    )
    profile_picture = models.ImageField(upload_to="profile/", blank=True, null=True)

    def is_customer(self):
        return self.role == Role.CUSTOMER

    def is_agent(self):
        return self.role == Role.AGENT

    def is_admin(self):
        return self.role == Role.ADMIN


class Department(models.Model):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        limit_choices_to={"role": Role.CUSTOMER},
        related_name="customer_profile"
    )
    solved_issues = models.PositiveIntegerField(default=0)
    is_paid = models.BooleanField(default=False)

    @classmethod
    def get_details(cls, username):
        try:
            profile = cls.objects.get(user__username=username)
            return model_to_dict(profile)
        except cls.DoesNotExist:
            return {"error": "Customer not found."}

    def save(self, *args, **kwargs):
        if not self.user.is_customer():
            raise ValueError("Only users with role='customer' can have a Customer profile.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Customer: {self.user.username}"


class Agent(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": Role.AGENT},
        related_name="agent_profile"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="agents"
    )
    current_customers = models.PositiveIntegerField(default=0)
    max_customers = models.PositiveIntegerField(default=5)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def has_capacity(self):
        return self.current_customers < self.max_customers

    @classmethod
    def get_details(cls, username):
        if not isinstance(username, str) or not username:
            return [CONTEXT_403]

        try:
            agent = cls.objects.select_related("user", "department").get(user__username=username)
            return {
                "id": agent.id,
                "department": agent.department.name,
                "username": agent.user.username,
                "current_customers": agent.current_customers,
                "max_customers": agent.max_customers,
                "is_available": agent.is_available,
            }
        except cls.DoesNotExist:
            return {"error": "Agent not found."}

    def save(self, *args, **kwargs):
        if not self.user.is_agent():
            raise ValueError("Only users with role='agent' can have an Agent profile.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Agent: {self.user.username} ({self.department.name})"


class Ticket(models.Model):
    ticket_id = models.CharField(max_length=16, unique=True, blank=True, null=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        related_name="tickets",
        null=True,
        blank=True
    )
    issue_title = models.CharField(max_length=100)
    issue_desc = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_ticket_details(cls, ticket_id):
        try:
            ticket = cls.objects.get(ticket_id=ticket_id)
            return model_to_dict(ticket)
        except cls.DoesNotExist:
            return {"error": "Ticket not found."}

    def __str__(self):
        return self.ticket_id or f"TID-{self.pk}"