"""
BaseRule is a base class for rules used for automation.

This abstract base class defines the structure and contract for automation rules
that can be applied to tickets. Subclasses must implement the abstract methods
to provide specific rule logic.

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""

from abc import ABC, abstractmethod


class BaseRule(ABC):
    """
    BaseRule is an abstract base class that defines the structure for automation rules.

    Attributes:
        ticket_id (Any): The identifier of the ticket to which the rule applies.
        params (dict): Additional parameters for the rule.

    Methods:
        should_apply():
            Abstract method to determine if the rule should be applied.
            Must be implemented by subclasses.

        apply():
            Abstract method to apply the rule logic.
            Must be implemented by subclasses.
    """

    def __init__(self, ticket, **kwargs):
        self.ticket_id = ticket
        self.params = kwargs

    @abstractmethod
    def should_apply(self):
        """
        Abstract method to determine if the rule should be applied.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def apply(self):
        """
        Abstract method to determine if the rule should be applied.
        Must be implemented by subclasses.
        """
        pass
