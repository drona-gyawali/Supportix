"""
RuleEngine is a class responsible for managing and executing a set of rules on a given ticket.
Attributes:
    ticket_id (int): The unique identifier of the ticket to which the rules will be applied.
    rules (list): A list of rule objects that define the logic to be executed.
Methods:
    __init__(ticket_id):
        Initializes the RuleEngine with a ticket ID and a predefined set of rules.
    run():
        Executes all the rules in the `rules` list. For each rule, it checks if the rule should be applied
        using the `should_apply` method. If applicable, it applies the rule using the `apply` method and
        collects the results in a context list. Returns the context containing details of applied rules.

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""

from core.automation.auto_close import AutoClose
from core.automation.tag_by_content import TagByContent


class RuleEngine:
    def __init__(self, ticket_id):
        self.ticket_id = ticket_id
        self.rules = [AutoClose(ticket_id, inactive_days=1), TagByContent(ticket_id)]

    def run(self):
        context = []
        for rule in self.rules:
            if rule.should_apply():
                result = rule.apply()
                context.append({"rule": rule.__class__.__name__, "details": result})
        return context
