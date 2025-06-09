import logging
import uuid

import stripe
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response

import core.validators as validators
from core.models import PaymentDetails, User
from main.settings import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET

logger = logging.getLogger(__name__)

stripe.api_key = STRIPE_SECRET_KEY


# Note: Stripe is not available in Nepal.
# Therefore, real-world testing is not possible.
# Only test cases can be provided as proof of functionality.
# This code is written in (2025-03-30)
class CreatePaymentIntentView(APIView):
    """
    API endpoint for creating a Stripe Payment Intent.

    This endpoint allows a user to create a payment intent by providing
    the amount, currency, and an optional description.

    Request Method:
        POST

    Request URL:
        /stripe/payments/intents/

    Example Request Body:
        {
            "amount": "10.00",
            "currency": "USD",
            "description": "Payment for order #123"
        }

    Response:
        200 OK
        {
            "client_secret": "<stripe_client_secret>",
            "payment_intent_id": "<stripe_payment_intent_id>"
        }

        400 Bad Request
        {
            "error": "<error_message>"
        }
    """

    def post(self, request, format=None):
        try:
            amount = request.data.get("amount")
            currency = request.data.get("currency", "").upper()
            description = request.data.get("description", "") or ""

            if currency not in validators.get_supported_currencies():
                return Response(
                    {"error": f"{currency} doesnot support"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if amount is None:
                return Response(
                    {"error": f"{amount} doesnot support."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                amount_cents = int(float(amount) * 100)
            except (ValueError, TypeError):
                return Response(
                    {"error": f"Invalid amount: {amount}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                description=description,
                metadata={"user_id": request.user.id},
                idempotency_key=str(uuid.uuid4()),
            )

            return Response(
                {"client_secret": intent.client_secret, "payment_intent_id": intent.id},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


stripe_payment = CreatePaymentIntentView.as_view()


class StripeWebhookView(APIView):
    """
    API endpoint for handling Stripe webhook events.
    This endpoint receives webhook events from Stripe, such as payment intent success or failure,
    and updates the corresponding payment records in the database.

    Request Method:
        POST

    Request URL:
        /api/stripe/webhooks/

    Headers:
        HTTP_STRIPE_SIGNATURE: Stripe signature for webhook verification

    Request Body:
        Raw JSON payload sent by Stripe containing event data.

    Example Event Types Handled:
        - payment_intent.succeeded
        - payment_intent.payment_failed

    Behavior:
        - On 'payment_intent.succeeded': Updates or creates a PaymentDetails record for the user and marks the payment as verified.
        - On 'payment_intent.payment_failed': Logs a warning for the failed payment.

    Responses:
        200 OK: Webhook processed successfully.
        400 Bad Request: Invalid payload or signature verification failed.
        404 Not Found: User associated with the payment intent does not exist.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return HttpResponse(status=400)

        obj = event["data"]["object"]
        intent_id = getattr(obj, "id", obj.get("id"))
        amount_cents = getattr(obj, "amount", obj.get("amount"))
        metadata = getattr(obj, "metadata", obj.get("metadata", {}))

        if event["type"] == "payment_intent.succeeded":
            user_id = metadata.get("user_id")
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return HttpResponse(status=404)

            amount = amount_cents / 100
            PaymentDetails.objects.update_or_create(
                stripe_payment_intent_id=intent_id,
                defaults={
                    "user": user,
                    "amount": amount,
                    "payment_verified": True,
                },
            )
            logger.info("Payment Success")

        elif event["type"] == "payment_intent.payment_failed":
            # TODO: some db logic can be perform btw: Unbound error
            logger.warning("Payment Failed")
        return HttpResponse(status=200)


stripe_payment_event = StripeWebhookView.as_view()
