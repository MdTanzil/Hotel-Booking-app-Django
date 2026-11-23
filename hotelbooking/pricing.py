"""Member-rate pricing.

Signed-in members pay 10% less on room stays. The discount is stored on
each booking at creation time (Booking.discount_rate), so a booking keeps
the price it was made at even if the member later signs out. Packages are
not discounted — they are already bundled deals.
"""

from decimal import Decimal

MEMBER_DISCOUNT_RATE = Decimal("0.10")


def member_discount_for(user):
    """The discount rate for a viewer: 10% when signed in, otherwise 0."""
    if getattr(user, "is_authenticated", False):
        return MEMBER_DISCOUNT_RATE
    return Decimal("0")


def discounted_price(price, discount_rate):
    """A nightly price after the discount, rounded to the cent."""
    return (
        Decimal(price) * (Decimal("1") - discount_rate)
    ).quantize(Decimal("0.01"))


def stay_total(price, nights, discount_rate):
    """Total for a stay of `nights` nights at `price` per night."""
    return discounted_price(price, discount_rate) * nights
