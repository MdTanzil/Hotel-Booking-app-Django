import random
from datetime import time
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField


def _generate_booking_reference():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "HB-" + "".join(random.choices(alphabet, k=6))


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(
        default=True,
        blank=True,
    )

    class Meta:
        abstract = True


class Room_category(BaseModel):
    name = models.CharField(max_length=100)
    desc = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Room_view(BaseModel):
    name = models.CharField(max_length=100)
    desc = models.TextField()

    def __str__(self):
        return self.name


class RoomAmenity(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Room(BaseModel):
    BED_KING = "king"
    BED_QUEEN = "queen"
    BED_TWIN = "twin"
    BED_DOUBLE = "double"
    BED_TYPE_CHOICES = [
        (BED_KING, "King"),
        (BED_QUEEN, "Queen"),
        (BED_TWIN, "Twin"),
        (BED_DOUBLE, "Double"),
    ]

    BATH_SHOWER = "shower"
    BATH_TUB = "tub"
    BATH_BOTH = "both"
    BATH_ROLLIN = "roll-in"
    BATHROOM_TYPE_CHOICES = [
        (BATH_SHOWER, "Walk-in shower"),
        (BATH_TUB, "Bathtub"),
        (BATH_BOTH, "Shower and bathtub"),
        (BATH_ROLLIN, "Roll-in shower"),
    ]

    room_name = models.CharField(max_length=50)
    room_price = models.DecimalField(max_digits=11, decimal_places=2)
    max_person = models.IntegerField(default=1)
    room_size = models.IntegerField()
    room_desc = RichTextField()
    room_category = models.ForeignKey(Room_category, on_delete=models.CASCADE)
    room_view = models.ManyToManyField(Room_view)
    room_bed = models.IntegerField(default=1)
    bed_type = models.CharField(
        max_length=10, choices=BED_TYPE_CHOICES, default=BED_KING
    )
    bathroom_type = models.CharField(
        max_length=10, choices=BATHROOM_TYPE_CHOICES, default=BATH_SHOWER
    )
    amenities = models.ManyToManyField(RoomAmenity, blank=True)
    whats_included = models.TextField(
        blank=True, help_text="One item per line."
    )
    room_image = models.ImageField(
        upload_to="rooms/", height_field=None, width_field=None, max_length=None
    )

    def __str__(self):
        return self.room_name

    @property
    def bed_label(self):
        noun = "bed" if self.room_bed == 1 else "beds"
        return f"{self.room_bed} {self.get_bed_type_display()} {noun}"

    @property
    def included_items(self):
        return [line.strip() for line in self.whats_included.splitlines() if line.strip()]


class Package_item(BaseModel):
    item_name = models.CharField(max_length=50)

    def __str__(self):
        return self.item_name


class Package(BaseModel):
    name = models.CharField(max_length=50)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    price = models.IntegerField(default=100)
    package_item = models.ManyToManyField(Package_item)
    description = models.TextField(blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    terms = models.TextField(blank=True, help_text="One term per line.")
    package_image = models.ImageField(
        "package", upload_to="packages/", height_field=None, width_field=None, max_length=None
    )

    def __str__(self):
        return self.name

    @property
    def is_current(self):
        today = timezone.localdate()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_to and today > self.valid_to:
            return False
        return True

    @property
    def validity_label(self):
        if self.valid_from and self.valid_to:
            return (
                f"Valid {self.valid_from.strftime('%d %b %Y')} – "
                f"{self.valid_to.strftime('%d %b %Y')}"
            )
        if self.valid_from:
            return f"Valid from {self.valid_from.strftime('%d %b %Y')}"
        if self.valid_to:
            return f"Valid until {self.valid_to.strftime('%d %b %Y')}"
        return ""

    @property
    def terms_list(self):
        return [line.strip() for line in self.terms.splitlines() if line.strip()]


class Booking(BaseModel):
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]
    PAYMENT_UNPAID = "unpaid"
    PAYMENT_PAID = "paid"
    PAYMENT_CHOICES = [
        (PAYMENT_UNPAID, "Unpaid"),
        (PAYMENT_PAID, "Paid"),
    ]
    PAY_AT_PROPERTY = "pay_at_property"
    PAY_ONLINE = "online"
    PAYMENT_METHOD_CHOICES = [
        (PAY_AT_PROPERTY, "Pay at the hotel"),
        (PAY_ONLINE, "Pay online now by card"),
    ]

    start_date = models.DateField()
    end_date = models.DateField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    guest_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, default="")
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=PAY_AT_PROPERTY,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="room_bookings",
    )
    reference = models.CharField(max_length=12, unique=True, null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_CONFIRMED
    )
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_CHOICES, default=PAYMENT_UNPAID
    )
    # Member-rate discount locked in when the booking was made (0.10 for
    # signed-in members, 0 for guests). See hotelbooking/pricing.py.
    discount_rate = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal("0")
    )

    @property
    def contact_email(self):
        if self.email:
            return self.email
        if self.user:
            return self.user.email
        return ""

    def stay_total_amount(self):
        """Total for this stay at the rate locked in at booking time."""
        from .pricing import stay_total

        nights = (self.end_date - self.start_date).days
        return stay_total(self.room.room_price, nights, self.discount_rate)

    def save(self, *args, **kwargs):
        if not self.reference:
            for _ in range(10):
                candidate = _generate_booking_reference()
                if not Booking.objects.filter(reference=candidate).exists():
                    self.reference = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.room.room_name


class Package_Booking(BaseModel):
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]
    PAYMENT_UNPAID = "unpaid"
    PAYMENT_PAID = "paid"
    PAYMENT_CHOICES = [
        (PAYMENT_UNPAID, "Unpaid"),
        (PAYMENT_PAID, "Paid"),
    ]
    PAY_AT_PROPERTY = "pay_at_property"
    PAY_ONLINE = "online"
    PAYMENT_METHOD_CHOICES = [
        (PAY_AT_PROPERTY, "Pay at the hotel"),
        (PAY_ONLINE, "Pay online now by card"),
    ]

    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)
    email = models.EmailField(blank=True, default="")
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=PAY_AT_PROPERTY,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="package_bookings",
    )
    reference = models.CharField(max_length=12, unique=True, null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_CONFIRMED
    )
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_CHOICES, default=PAYMENT_UNPAID
    )

    @property
    def contact_email(self):
        if self.email:
            return self.email
        if self.user:
            return self.user.email
        return ""

    def save(self, *args, **kwargs):
        if not self.reference:
            for _ in range(10):
                candidate = _generate_booking_reference()
                if not Package_Booking.objects.filter(reference=candidate).exists():
                    self.reference = candidate
                    break
        super().save(*args, **kwargs)


class Review(BaseModel):
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="room_reviews",
    )
    guest_name = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField(max_length=1000)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["room", "user"],
                condition=models.Q(user__isnull=False),
                name="unique_room_review_per_user",
            )
        ]

    def __str__(self):
        return f"{self.guest_name} - {self.room.room_name} ({self.rating}/5)"


class Guest(BaseModel):
    guest_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    nid_number = models.IntegerField(default=0)
    passport = models.CharField(max_length=15)
    permanent_address = models.TextField(blank=True)
    post_code = models.CharField(max_length=5)

    def __str__(self):
        return self.guest_name


class Lead(BaseModel):
    """A group/wedding/event enquiry (RFP) from the contact page."""

    EVENT_WEDDING = "wedding"
    EVENT_CORPORATE = "corporate"
    EVENT_FAMILY = "family"
    EVENT_GROUP = "group"
    EVENT_OTHER = "other"
    EVENT_CHOICES = [
        (EVENT_WEDDING, "Wedding"),
        (EVENT_CORPORATE, "Corporate / business"),
        (EVENT_FAMILY, "Family gathering"),
        (EVENT_GROUP, "Group stay"),
        (EVENT_OTHER, "Other event"),
    ]
    STATUS_NEW = "new"
    STATUS_CONTACTED = "contacted"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_CLOSED, "Closed"),
    ]

    name = models.CharField(max_length=100, default="")
    email = models.EmailField(default="")
    phone_number = models.CharField(max_length=20, blank=True, default="")
    event_type = models.CharField(
        max_length=10, choices=EVENT_CHOICES, default=EVENT_GROUP
    )
    start_date = models.DateField()
    end_date = models.DateField()
    adult_member = models.IntegerField(default=1)
    child = models.IntegerField(default=0)
    rooms_needed = models.IntegerField(default=1)
    message = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_NEW
    )

    def __str__(self):
        return f"{self.name} — {self.get_event_type_display()} ({self.start_date})"

class Contact(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    def __str__(self):
        return self.name

class BlogPost(BaseModel):
    CATEGORY_GUIDE = "guide"
    CATEGORY_EVENT = "event"
    CATEGORY_HOTEL = "hotel"
    CATEGORY_DINING = "dining"
    CATEGORY_CHOICES = [
        (CATEGORY_GUIDE, "Guide"),
        (CATEGORY_EVENT, "Event"),
        (CATEGORY_HOTEL, "Hotel news"),
        (CATEGORY_DINING, "Dining"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.CharField(
        max_length=10, choices=CATEGORY_CHOICES, default=CATEGORY_HOTEL
    )
    excerpt = models.CharField(max_length=300)
    body = models.TextField(help_text="Plain text; blank lines separate paragraphs.")
    # Path of a theme image under static/images/, e.g. "images/image_1.jpg".
    image = models.CharField(max_length=200, default="images/bg_1.jpg")
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("hotelbooking:blog-detail", args=[self.slug])


class TableBooking(BaseModel):
    """A restaurant table reservation from the Book a Table form."""

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]
    TIME_CHOICES = [
        (time(12, 0), "12:00 PM"),
        (time(12, 30), "12:30 PM"),
        (time(13, 0), "1:00 PM"),
        (time(13, 30), "1:30 PM"),
        (time(14, 0), "2:00 PM"),
        (time(18, 0), "6:00 PM"),
        (time(18, 30), "6:30 PM"),
        (time(19, 0), "7:00 PM"),
        (time(19, 30), "7:30 PM"),
        (time(20, 0), "8:00 PM"),
        (time(20, 30), "8:30 PM"),
        (time(21, 0), "9:00 PM"),
    ]

    name = models.CharField(max_length=100, default="")
    email = models.EmailField(default="")
    phone_number = models.CharField(max_length=20, blank=True, default="")
    date = models.DateField()
    time = models.TimeField(choices=TIME_CHOICES)
    guests = models.IntegerField(default=2)
    occasion = models.CharField(max_length=100, blank=True, default="")
    message = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING
    )

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        return f"{self.name} — {self.date} {self.time} ({self.guests} guests)"
