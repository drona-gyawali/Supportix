from django.db import models
from django.forms import model_to_dict
from django.contrib.auth.models import User
from .dumps import STATUS_CHOICES, ROLE, CONTEXT_403


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profile/", blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE, default="customer")

    def __str__(self):
        return self.user.username


class Department(models.Model):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    customer_name = models.ForeignKey(
        UserDetails,
        on_delete=models.CASCADE,
        related_name="customer_name",
        blank=True,
        null=True,
    )
    solved_issue = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)

    @classmethod
    def get_details(cls, customer_name):
        try:
            customer_details = cls.objects.get(
                customer_name__user__username=customer_name
            )
            return model_to_dict(customer_details)
        except cls.DoesNotExist:
            return {"error": "customer Not Found."}

    def save(self, *args, **kwargs):
        if self.customer_name.role != "customer":
            raise ValueError(
                "Only users with the role 'customer' can be assigned as customer."
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.customer_name.user.username


class Agents(models.Model):
    dept_name = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="department"
    )
    agent_name = models.ForeignKey(
        UserDetails,
        on_delete=models.CASCADE,
        related_name="agent_name",
        blank=True,
        null=True,
    )
    current_customer = models.IntegerField(default=0)
    max_customer = models.IntegerField(default=1)
    is_available = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.agent_name.role != "agent":
            raise ValueError(
                "Only users with the role 'agent' can be assigned as agents."
            )
        super().save(*args, **kwargs)

    @classmethod
    def get_details(cls, agent_name):
        if not isinstance(agent_name, str) or agent_name == "":
            return {CONTEXT_403}

        try:
            agent_details = cls.objects.select_related("agent_name").get(
                agent_name__user__username=agent_name
            )
            return {
                "id": agent_details.id,
                "dept_name": (
                    agent_details.dept_name.name if agent_details.dept_name else None
                ),
                "agent_name": (
                    agent_details.agent_name.user.username
                    if agent_details.agent_name
                    else None
                ),
                "current_customer": agent_details.current_customer,
                "max_customer": agent_details.max_customer,
                "is_available": agent_details.is_available,
            }
        except cls.DoesNotExist:
            return {"Error": "Agent Not Found."}

    @property
    def has_capacity(self):
        return self.current_customer < self.max_customer

    def __str__(self):
        return f"{self.id} - {self.agent_name.user.username} (Customers: {self.current_customer}/{self.max_customer})"


class Ticket(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="customer_tickets",
        blank=True,
        null=True,
    )
    agents = models.ForeignKey(
        Agents,
        on_delete=models.CASCADE,
        related_name="ticket_to_customer",
        blank=True,
        null=True,
    )
    ticket_id = models.CharField(max_length=16, unique=True, blank=True, null=True)
    issue_title = models.CharField(max_length=100)
    issue_desc = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="waiting")
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_ticket_details(cls, ticket_id):
        try:
            ticket = cls.objects.get(ticket_id=ticket_id)
            return model_to_dict(ticket)
        except cls.DoesNotExist:
            return {"Ticket not Found"}

    def __str__(self):
        return self.ticket_id
