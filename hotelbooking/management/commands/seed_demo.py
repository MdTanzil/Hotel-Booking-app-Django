"""Seed demo rooms and packages so a fresh deployment is not empty.

Room and package photos are copied from the theme images already in
static/images/ into MEDIA_ROOT. Run automatically by build.py on Vercel;
safe to run locally too:

    python manage.py seed_demo --if-empty

The command is idempotent: it never creates duplicate rows, and it
re-copies any photo whose file is missing. That second part matters on
Vercel: media/ is not in git, so every build starts with no photo files
at all — even when the database already has the rooms, their photos
must be copied again or the live pages show broken images.
"""

from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from hotelbooking.models import (
    Package,
    Package_item,
    Review,
    Room,
    RoomAmenity,
    Room_category,
    Room_view,
)

STATIC_IMAGES = Path(settings.BASE_DIR) / "static" / "images"

CATEGORIES = [
    ("Deluxe", "Comfortable rooms with modern amenities for a relaxing stay."),
    ("Executive", "Spacious rooms with a work desk and premium facilities."),
    ("Family", "Large rooms that comfortably fit the whole family."),
    ("Suite", "Our finest suites with a separate living area and top views."),
]

VIEWS = [
    ("Sea View", "Wake up to a view over the water."),
    ("City View", "A sweeping view across the city skyline."),
    ("Garden View", "A calm view over the hotel gardens."),
    ("Pool View", "Overlooking the outdoor swimming pool."),
]

AMENITIES = [
    "Free Wi-Fi",
    "Air conditioning",
    "Flat-screen TV",
    "Mini fridge",
    "Coffee maker",
    "In-room safe",
    "Hair dryer",
    "Work desk",
    "Blackout curtains",
    "Private balcony",
    "Room service",
]

# name, price (BDT/night), max_person, size (sqm), beds, bed type, bathroom
# type, category, views, image, description, amenities, what's included
ROOMS = [
    (
        "Deluxe King Room",
        8500,
        2,
        35,
        1,
        "king",
        "shower",
        "Deluxe",
        ["City View"],
        "room-1.jpg",
        "A bright, comfortable room with a king bed, rainfall shower and "
        "a quiet corner to unwind after a day out.",
        ["Free Wi-Fi", "Air conditioning", "Flat-screen TV", "Coffee maker",
         "In-room safe", "Hair dryer"],
        "Daily housekeeping\nComplimentary bottled water\n"
        "Access to the outdoor pool\nFree on-site parking",
    ),
    (
        "Executive Twin Room",
        12000,
        2,
        42,
        2,
        "twin",
        "shower",
        "Executive",
        ["City View", "Pool View"],
        "room-2.jpg",
        "Two comfortable beds, a proper work desk and fast Wi-Fi — ideal "
        "for business trips and friends travelling together.",
        ["Free Wi-Fi", "Air conditioning", "Flat-screen TV", "Work desk",
         "Coffee maker", "In-room safe"],
        "Daily housekeeping\nComplimentary bottled water\n"
        "Work desk with task lighting\nAccess to the outdoor pool",
    ),
    (
        "Family Suite",
        18000,
        4,
        60,
        2,
        "queen",
        "both",
        "Family",
        ["Garden View"],
        "room-3.jpg",
        "Plenty of space for the whole family, with two bedrooms, a "
        "sitting area and a garden-facing balcony.",
        ["Free Wi-Fi", "Air conditioning", "Flat-screen TV", "Mini fridge",
         "Coffee maker", "In-room safe", "Hair dryer"],
        "Daily housekeeping\nComplimentary bottled water\n"
        "Garden-facing balcony\nAccess to the outdoor pool and kids' area",
    ),
    (
        "Premium Suite",
        25000,
        3,
        75,
        1,
        "king",
        "both",
        "Suite",
        ["Sea View", "Pool View"],
        "room-4.jpg",
        "Our finest suite: a separate living room, a soaking tub and "
        "floor-to-ceiling windows over the sea.",
        ["Free Wi-Fi", "Air conditioning", "Flat-screen TV", "Mini fridge",
         "Coffee maker", "In-room safe", "Hair dryer", "Private balcony",
         "Room service"],
        "Daily housekeeping\nWelcome drink on arrival\n"
        "Soaking tub and sea-facing lounge\nAccess to the outdoor pool and spa",
    ),
    (
        "Deluxe Queen Room",
        9500,
        2,
        38,
        1,
        "queen",
        "tub",
        "Deluxe",
        ["Garden View"],
        "room-5.jpg",
        "A calm queen room looking over the gardens, with a deep soaking "
        "tub and blackout curtains for a good night's sleep.",
        ["Free Wi-Fi", "Air conditioning", "Flat-screen TV", "Coffee maker",
         "In-room safe", "Hair dryer", "Blackout curtains"],
        "Daily housekeeping\nComplimentary bottled water\n"
        "Deep soaking tub\nAccess to the outdoor pool",
    ),
    (
        "Executive King Suite",
        22000,
        3,
        68,
        1,
        "king",
        "both",
        "Executive",
        ["Sea View"],
        "room-6.jpg",
        "A king suite with a sea-facing lounge, a work area and a "
        "private balcony for evening coffee.",
        ["Free Wi-Fi", "Air conditioning", "Flat-screen TV", "Mini fridge",
         "Work desk", "Coffee maker", "In-room safe", "Hair dryer",
         "Private balcony"],
        "Daily housekeeping\nComplimentary bottled water\n"
        "Sea-facing lounge and work area\nAccess to the outdoor pool",
    ),
]

PACKAGE_ITEMS = [
    "Complimentary Breakfast",
    "Airport Pickup",
    "Spa Access",
    "Free Wi-Fi",
    "Swimming Pool",
    "Guided City Tour",
]

# name, room name, price (BDT), items, image
PACKAGES = [
    (
        "Weekend Getaway",
        "Family Suite",
        32000,
        ["Complimentary Breakfast", "Swimming Pool", "Guided City Tour"],
        "image_1.jpg",
    ),
    (
        "Honeymoon Special",
        "Premium Suite",
        45000,
        ["Complimentary Breakfast", "Spa Access", "Airport Pickup"],
        "image_2.jpg",
    ),
]


DEMO_PASSWORD = "demo1234"

# Sample guest reviews shown on room pages and the home page.
# These are fictional demo content for the demo hotel.
# room name, guest name, rating (1-5), text
REVIEWS = [
    (
        "Deluxe King Room",
        "Sarah M.",
        5,
        "Spotless room, a very comfortable bed and quiet at night. "
        "Check-in took two minutes. Would happily stay again.",
    ),
    (
        "Deluxe King Room",
        "Rahim U.",
        4,
        "Great value for the price. The shower pressure could be better, "
        "but the room itself was clean and the staff were friendly.",
    ),
    (
        "Premium Suite",
        "Elena R.",
        5,
        "The sea view from the suite is worth every penny. Breakfast was "
        "excellent and the staff arranged a late checkout for us.",
    ),
    (
        "Family Suite",
        "James L.",
        5,
        "Plenty of space for two adults and two kids, and the garden "
        "balcony was perfect for evening tea. Highly recommended.",
    ),
    (
        "Executive Twin Room",
        "Priya K.",
        4,
        "Good desk setup and fast Wi-Fi for working. A little street noise "
        "in the morning, but overall a solid business stay.",
    ),
    (
        "Executive King Suite",
        "Daniel O.",
        5,
        "Beautiful suite and the private balcony at sunset is something "
        "else. The team even helped us book a local tour.",
    ),
    (
        "Deluxe Queen Room",
        "Nadia H.",
        4,
        "Calm room overlooking the gardens, very dark and quiet for "
        "sleeping. Would have liked a few more power outlets.",
    ),
    (
        "Family Suite",
        "Tom W.",
        3,
        "Roomy and clean, but the air conditioning was noisy on the first "
        "night. Staff fixed it the next morning.",
    ),
]


# Demo accounts shown on the login page so visitors can try the site.
# username, email, display name, is_staff, is_superuser
DEMO_USERS = [
    ("admin", "admin@demo.hotel", "Demo Admin", True, True),
    ("staff", "staff@demo.hotel", "Demo Staff", True, False),
    ("guest", "guest@demo.hotel", "Demo Guest", False, False),
]


class Command(BaseCommand):
    help = (
        "Seed demo room categories, views, rooms, packages and demo "
        "accounts. Idempotent: never duplicates rows, and re-copies any "
        "photo whose file is missing."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--if-empty",
            action="store_true",
            help=(
                "Accepted for compatibility; the command is idempotent, "
                "so rows are never duplicated, and photos are always "
                "ensured even when the rooms already exist."
            ),
        )

    def handle(self, *args, **options):
        categories = {
            name: Room_category.objects.get_or_create(
                name=name, defaults={"desc": desc}
            )[0]
            for name, desc in CATEGORIES
        }
        views = {
            name: Room_view.objects.get_or_create(name=name, defaults={"desc": desc})[
                0
            ]
            for name, desc in VIEWS
        }

        rooms = {}
        amenities = {
            name: RoomAmenity.objects.get_or_create(name=name)[0]
            for name in AMENITIES
        }
        for (
            name,
            price,
            persons,
            size,
            beds,
            bed_type,
            bathroom_type,
            cat,
            view_names,
            image,
            desc,
            amenity_names,
            included,
        ) in ROOMS:
            room, _created = Room.objects.get_or_create(
                room_name=name,
                defaults={
                    "room_price": price,
                    "max_person": persons,
                    "room_size": size,
                    "room_bed": beds,
                    "room_category": categories[cat],
                    "room_desc": f"<p>{desc}</p>",
                },
            )
            # Set on every run (not just on create) so rooms seeded before
            # these fields existed still get them.
            room.bed_type = bed_type
            room.bathroom_type = bathroom_type
            room.whats_included = included
            room.save()
            room.room_view.set(views[v] for v in view_names)
            room.amenities.set(amenities[a] for a in amenity_names)
            self._ensure_image(room.room_image, image)
            rooms[name] = room
            self.stdout.write(f"Room: {name}")

        items = {
            name: Package_item.objects.get_or_create(item_name=name)[0]
            for name in PACKAGE_ITEMS
        }
        for name, room_name, price, item_names, image in PACKAGES:
            package, _created = Package.objects.get_or_create(
                name=name,
                defaults={"room": rooms[room_name], "price": price},
            )
            package.package_item.set(items[i] for i in item_names)
            self._ensure_image(package.package_image, image)
            self.stdout.write(f"Package: {name}")

        for room_name, guest_name, rating, text in REVIEWS:
            Review.objects.get_or_create(
                room=rooms[room_name],
                guest_name=guest_name,
                defaults={"rating": rating, "text": text},
            )
            self.stdout.write(f"Review: {guest_name} on {room_name}")

        self._seed_demo_users()

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))

    def _ensure_image(self, field_file, filename):
        """Copy the seed photo into media unless its file is already there.

        The database row may survive from an earlier deployment while the
        file does not (media/ is not in git, so each Vercel build starts
        with an empty media folder). Checking the file, not just the row,
        is what keeps live photos working after every deploy.
        """
        if field_file and default_storage.exists(field_file.name):
            return
        field_file.save(filename, ContentFile(self._image_bytes(filename)))

    def _seed_demo_users(self):
        """Create the demo accounts shown on the login page.

        Passwords are reset on every run so the published demo logins
        keep working even if a visitor changes one. An account is only
        ever touched when its email matches the demo address: if a real
        visitor registered the same username first, it is left alone.
        """
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Permission

        User = get_user_model()
        for username, email, display_name, is_staff, is_superuser in DEMO_USERS:
            existing = User.objects.filter(username=username).first()
            if existing and existing.email != email:
                self.stdout.write(
                    self.style.WARNING(
                        f"User '{username}' exists with a different email; "
                        "leaving it alone."
                    )
                )
                continue
            user, _created = User.objects.update_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": display_name,
                    "is_staff": is_staff,
                    "is_superuser": is_superuser,
                    "is_active": True,
                },
            )
            user.set_password(DEMO_PASSWORD)
            user.save()
            if is_staff and not is_superuser:
                # Staff can explore the admin and manage bookings, but
                # cannot delete anything or manage users.
                perms = Permission.objects.filter(
                    content_type__app_label="hotelbooking",
                    codename__regex=r"^(view|add|change)_",
                )
                user.user_permissions.set(perms)
            role = (
                "superuser" if is_superuser else "staff" if is_staff else "user"
            )
            self.stdout.write(f"Demo user: {username} ({role})")

    @staticmethod
    def _image_bytes(filename):
        path = STATIC_IMAGES / filename
        if not path.exists():
            raise FileNotFoundError(f"Seed image not found: {path}")
        return path.read_bytes()
