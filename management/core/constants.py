"""
This module defines constants used across the Support System application.

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""

from django.db import models


class Role(models.TextChoices):
    """Possible type of roles that can be choosen

    * Agent: Interact with customers to solve the issue .
    * Customer: Interact with Agent to help with the issue.
    * Admin: Manage both customer and Agent level settings.
    """

    CUSTOMER = "customer", "Customer"
    AGENT = "agent", "Agent"
    ADMIN = "admin", "Admin"


class Status(models.TextChoices):
    """Possible statuses for tasks or tickets

    * Waiting: Task is waiting to be processed.
    * Assigned: Task has been assigned to an agent.
    * Progress: Task is currently in progress.
    * Completed: Task has been completed.
    * Closed: Task has been closed.
    """

    WAITING = "waiting", "Waiting"
    ASSIGNED = "assigned", "Assigned"
    PROGRESS = "progress", "Progress"
    COMPLETED = "completed", "Completed"
    CLOSED = "closed", "Closed"


class Reaction(models.TextChoices):
    """Possible reactions for content or messages.

    * LIKE: 👍 Like - Expresses general approval or agreement.
    * LOVE: ❤️ Love - Expresses strong affection or appreciation.
    * LAUGH: 😂 Laugh - Indicates something is funny or amusing.
    * SAD: 😢 Sad - Expresses sympathy or sadness.
    * ANGRY: 😡 Angry - Shows disapproval or frustration..
    * ROCKET: 🚀 Rocket - Shows succuess or high qualty deliverables
    """

    LIKE = "like", "👍"
    LOVE = "love", "❤️"
    LAUGH = "laugh", "😂"
    SAD = "sad", "😢"
    ANGRY = "angry", "😡"
    ROCKET = "rocket", "🚀"
