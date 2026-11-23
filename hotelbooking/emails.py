"""Booking emails. Sending must never break a booking: a missing address
or a mail failure is logged and the booking flow continues."""

import logging
from datetime import date

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _nights(booking):
    start, end = booking.start_date, booking.end_date
    if isinstance(start, str):
        start = date.fromisoformat(start)
    if isinstance(end, str):
        end = date.fromisoformat(end)
    return (end - start).days


def _send(to_email, subject, template, context):
    if not to_email:
        return False
    try:
        send_mail(
            subject,
            render_to_string(template, context),
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False


def _contact_email(booking):
    return booking.contact_email


def send_booking_confirmation(booking):
    nights = _nights(booking)
    return _send(
        _contact_email(booking),
        f"Your booking is confirmed - {booking.reference}",
        "hotelbooking/emails/booking_confirmation.txt",
        {
            "booking": booking,
            "nights": nights,
            "total": booking.stay_total_amount(),
        },
    )


def send_package_booking_confirmation(booking):
    return _send(
        _contact_email(booking),
        f"Your package booking is confirmed - {booking.reference}",
        "hotelbooking/emails/package_booking_confirmation.txt",
        {"booking": booking},
    )


def send_booking_cancellation(booking):
    return _send(
        _contact_email(booking),
        f"Your booking is cancelled - {booking.reference}",
        "hotelbooking/emails/booking_cancellation.txt",
        {"booking": booking},
    )


def send_package_booking_cancellation(booking):
    return _send(
        _contact_email(booking),
        f"Your package booking is cancelled - {booking.reference}",
        "hotelbooking/emails/package_booking_cancellation.txt",
        {"booking": booking},
    )


def send_booking_dates_changed(booking):
    nights = _nights(booking)
    return _send(
        _contact_email(booking),
        f"Your booking dates changed - {booking.reference}",
        "hotelbooking/emails/booking_dates_changed.txt",
        {
            "booking": booking,
            "nights": nights,
            "total": booking.stay_total_amount(),
        },
    )
