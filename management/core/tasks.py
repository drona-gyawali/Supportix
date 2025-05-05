from celery import shared_task


# testing the celery
@shared_task
def send_welcome_email(user_email):
    # Simulating sending an email
    print(f"Sending welcome email to {user_email}")
    return f"Email sent to {user_email}"

# Todo
@shared_task
def _delete_completed_ticketid():
    pass