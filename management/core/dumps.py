# core.models <Tickets>
STATUS_CHOICES = [
    ("waiting", "Waiting"),
    ("assigned", "Assigned"),
    ("progress", "Progress"),
    ("completed", "Completed"),
]
# core.models <UserDetails>
ROLE = [
    ("agent", "Agent"),
    ("customer", "Customer"),
]

SUCESS_SIGNUP = {"User created Successfully"}
CONTEXT_400 = {"Invalid credentials"}
CONTEXT_405 = {"Request method not allowed."}
CONTEXT_403 = {"Unauthorized access."}
