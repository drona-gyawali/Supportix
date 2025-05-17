"""
Core models for the application, managing user roles, departments, customers,
agents, and tickets. Defines business logic and data relationships.

Classes:
    User(AbstractUser): Extends Django's AbstractUser with role and profile picture.
    Department: Represents organizational departments.
    Customer: Customer profile linked to a user with role 'customer'.
    Agent: Agent profile linked to a user with role 'agent'.
    Ticket: Support ticket with details like customer, agent, and status.

Constants:
    STATUS_CHOICES: Ticket statuses (e.g., waiting, resolved).
    ROLE: User roles (e.g., customer, agent, admin).
    CONTEXT_403: Forbidden context for invalid operations.

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""

from datetime import timezone

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import model_to_dict

from core.constants import Role, Status
from core.dumps import CONTEXT_403


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        help_text="Defines the user's role: customer, agent, or admin.",
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
        related_name="customer_profile",
    )
    solved_issues = models.PositiveIntegerField(default=0)
    is_paid = models.BooleanField(default=False)

    @classmethod
    def get_details(cls, username):
        try:
            profile = cls.objects.select_related("user").get(user__username=username)
            data = model_to_dict(profile)
            data["username"] = profile.user.username
            data["name"] = f"{profile.user.first_name} {profile.user.last_name}".strip()
            return data
        except cls.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if not self.user.is_customer():
            raise ValueError(
                "Only users with role='customer' can have a Customer profile."
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Customer: {self.user.username}"


class Agent(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": Role.AGENT},
        related_name="agent_profile",
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="agents"
    )
    current_customers = models.PositiveIntegerField(default=0)
    max_customers = models.PositiveIntegerField(default=5)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def has_capacity(self) -> property:
        return self.current_customers < self.max_customers

    @classmethod
    def get_details(cls, username):
        if not isinstance(username, str) or not username:
            return [CONTEXT_403]

        try:
            agent = cls.objects.select_related("user", "department").get(
                user__username=username
            )
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
        Customer, on_delete=models.CASCADE, related_name="tickets"
    )
    agent = models.ForeignKey(
        Agent, on_delete=models.SET_NULL, related_name="tickets", null=True, blank=True
    )
    issue_title = models.CharField(max_length=100)
    issue_desc = models.TextField(blank=True, null=True)
    tag = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.WAITING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    queued_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def get_ticket_details(cls, ticket_id):
        try:
            ticket = cls.objects.get(ticket_id=ticket_id)
            return model_to_dict(ticket)
        except cls.DoesNotExist:
            return {"error": "Ticket not found."}

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ticket_id or f"TID-{self.pk}"


class StatusChange(models.Model):
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="status_changes"
    )
    new_status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.WAITING
    )
    updated_at = models.DateTimeField(auto_now_add=True)
    new_queued_at = models.DateTimeField(null=True, blank=True)
    new_agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        related_name="status_changes",
        null=True,
        blank=True,
    )


class AutoEscalate(models.Model):
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="auto_escalate"
    )
    status_change = models.ForeignKey(
        StatusChange, on_delete=models.CASCADE, related_name="auto_escalate"
    )

    @classmethod
    def escalate_changes(cls, ticket_id, new_status, new_agent=None):
        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id)
            status_change = StatusChange.objects.create(
                new_status=new_status,
                new_agent=new_agent,
                new_queued_at=timezone.now(),
            )
            cls.objects.create(ticket=ticket, status_changes=status_change)
            ticket.status = new_status
            if new_agent:
                ticket.agent = new_agent
            ticket.save()
            return {"success": True, "message": f"Ticket {ticket_id} escalated."}
        except Ticket.DoesNotExist:
            return {
                "success": False,
                "message": f"Ticket series {ticket_id} not found.",
            }
        except Exception as e:
            return {"success": False, "message": f"Error during escalation: {str(e)}"}
