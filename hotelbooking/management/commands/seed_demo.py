"""Seed demo rooms and packages so a fresh deployment is not empty.

Room and package photos are copied from the theme images already in
static/images/ into MEDIA_ROOT. Run automatically by build.py on Vercel;
safe to run locally too:

    python manage.py seed_demo --if-empty
"""

from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from hotelbooking.models import (
    Package,
    Package_item,
    Room,
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

# name, price (BDT/night), max_person, size (sqm), beds, category, views, image
ROOMS = [
    (
        "Deluxe King Room",
        8500,
        2,
        35,
        1,
        "Deluxe",
        ["City View"],
        "room-1.jpg",
        "A bright, comfortable room with a king bed, rainfall shower and "
        "a quiet corner to unwind after a day out.",
    ),
    (
        "Executive Twin Room",
        12000,
        2,
        42,
        2,
        "Executive",
        ["City View", "Pool View"],
        "room-2.jpg",
        "Two comfortable beds, a proper work desk and fast Wi-Fi — ideal "
        "for business trips and friends travelling together.",
    ),
    (
        "Family Suite",
        18000,
        4,
        60,
        2,
        "Family",
        ["Garden View"],
        "room-3.jpg",
        "Plenty of space for the whole family, with two bedrooms, a "
        "sitting area and a garden-facing balcony.",
    ),
    (
        "Premium Suite",
        25000,
        3,
        75,
        1,
        "Suite",
        ["Sea View", "Pool View"],
        "room-4.jpg",
        "Our finest suite: a separate living room, a soaking tub and "
        "floor-to-ceiling windows over the sea.",
    ),
    (
        "Deluxe Queen Room",
        9500,
        2,
        38,
        1,
        "Deluxe",
        ["Garden View"],
        "room-5.jpg",
        "A calm queen room looking over the gardens, with a deep soaking "
        "tub and blackout curtains for a good night's sleep.",
    ),
    (
        "Executive King Suite",
        22000,
        3,
        68,
        1,
        "Executive",
        ["Sea View"],
        "room-6.jpg",
        "A king suite with a sea-facing lounge, a work area and a "
        "private balcony for evening coffee.",
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


class Command(BaseCommand):
    help = "Seed demo room categories, views, rooms and packages."

    def add_arguments(self, parser):
        parser.add_argument(
            "--if-empty",
            action="store_true",
            help="Only seed when no rooms exist yet.",
        )

    def handle(self, *args, **options):
        if options["if_empty"] and Room.objects.exists():
            self.stdout.write("Rooms already exist, skipping seed.")
            return

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
        for name, price, persons, size, beds, cat, view_names, image, desc in ROOMS:
            room, created = Room.objects.get_or_create(
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
            room.room_view.set(views[v] for v in view_names)
            if created or not room.room_image:
                room.room_image.save(image, ContentFile(self._image_bytes(image)))
            rooms[name] = room
            self.stdout.write(f"Room: {name}")

        items = {
            name: Package_item.objects.get_or_create(item_name=name)[0]
            for name in PACKAGE_ITEMS
        }
        for name, room_name, price, item_names, image in PACKAGES:
            package, created = Package.objects.get_or_create(
                name=name,
                defaults={"room": rooms[room_name], "price": price},
            )
            package.package_item.set(items[i] for i in item_names)
            if created or not package.package_image:
                package.package_image.save(
                    image, ContentFile(self._image_bytes(image))
                )
            self.stdout.write(f"Package: {name}")

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))

    @staticmethod
    def _image_bytes(filename):
        path = STATIC_IMAGES / filename
        if not path.exists():
            raise FileNotFoundError(f"Seed image not found: {path}")
        return path.read_bytes()
