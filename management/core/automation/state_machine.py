"""
This module defines a state transition system for managing ticket status transitions.
It includes logic to determine if a state change is valid and to perform the transition.

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""


class TicketStateMachine:
    def __init__(self, ticket):
        self.ticket_id = ticket.id

    def can_state_change(self, new_status):
        transition = {
            "waiting": ["assigned", "closed", "completed", "progress"],
            "assigned": ["waiting", "completed", "closed"],
            "progress": ["waiting", "closed", "completed", "assigned"],
            "completed": ["waiting", "closed"],
            "closed": [],
        }
        return new_status in transition.get(self.ticket.status, [])

    def transition_to(self, new_status):
        if self.can_state_change(new_status):
            self.ticket.status = new_status
            self.ticket.save()
            return True
        return False
