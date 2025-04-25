"""
Info:
  Copyright (c) Support System
  Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
  
This module defines constants used across the Support System application.
"""
from django.db import models

class Role(models.TextChoices):
    """Possible type of roles that can be choosen

    * Agent: Interact with customers to solve the issue .
    * Customer: Interact with Agent to help with the issue.
    * Admin: Manage both customer and Agent level settings.
    """
    CUSTOMER = "customer",
    AGENT = "agent"
    ADMIN = "admin"

class Status(models.TextChoices):
    """Possible statuses for tasks or tickets

    * Waiting: Task is waiting to be processed.
    * Assigned: Task has been assigned to an agent.
    * Progress: Task is currently in progress.
    * Completed: Task has been completed.
    """
    WAITING = "waiting", "Waiting"
    ASSIGNED = "assigned", "Assigned"
    PROGRESS = "progress", "Progress"
    COMPLETED = "completed", "Completed"