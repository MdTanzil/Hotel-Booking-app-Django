"""Stripe Checkout (test mode) for booking payments. Amounts always come
from the database, never from the client. Payments stay disabled until
STRIPE_SECRET_KEY is set."""

import stripe
from decimal import Decimal

from django.conf import settings
from django.urls import reverse

from .models import Booking, Package_Booking


def stripe_configured():
    return bool(settings.STRIPE_SECRET_KEY)


def stripe_get(obj, key, default=None):
    """Read a key from a dict or a Stripe object (Stripe objects in v7+
    do not support .get())."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _amount_cents(amount):
    return int((Decimal(amount) * 100).to_integral_value())


def booking_amount(booking):
    """Amount to charge for a room booking, at the rate locked in when
    the booking was made (member rate if it was booked signed in)."""
    return booking.stay_total_amount()


def create_checkout_session(request, booking, kind):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if kind == "room":
        name = (
            f"{booking.room.room_name} "
            f"({booking.start_date} to {booking.end_date})"
        )
        amount = booking_amount(booking)
    else:
        name = f"{booking.package.name} package"
        amount = booking.package.price
    success_url = request.build_absolute_uri(
        reverse("hotelbooking:payment-success")
    ) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(
        reverse("hotelbooking:payment-cancel")
    )
    return stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": _amount_cents(amount),
                    "product_data": {"name": f"Deluxe Hotel - {name}"},
                },
                "quantity": 1,
            }
        ],
        metadata={
            "booking_type": kind,
            "booking_id": str(booking.pk),
            "reference": booking.reference or "",
        },
        success_url=success_url,
        cancel_url=cancel_url,
    )


def mark_booking_paid(session):
    """Mark the booking behind a paid Checkout Session as paid.

    Idempotent: calling it twice (success page + webhook) is safe.
    Returns the booking, or None if the session has no known booking.
    """
    metadata = stripe_get(session, "metadata") or {}
    kind = stripe_get(metadata, "booking_type")
    booking_id = stripe_get(metadata, "booking_id")
    if kind not in ("room", "package") or not booking_id:
        return None
    model = Booking if kind == "room" else Package_Booking
    try:
        booking = model.objects.get(pk=booking_id)
    except model.DoesNotExist:
        return None
    if booking.payment_status != model.PAYMENT_PAID:
        booking.payment_status = model.PAYMENT_PAID
        booking.save(update_fields=["payment_status", "updated_at"])
    return booking
