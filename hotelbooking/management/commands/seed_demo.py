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

from datetime import date, timedelta

from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from hotelbooking.models import (
    BlogPost,
    Event,
    HeroSlide,
    Package,
    Package_item,
    Review,
    Room,
    RoomAmenity,
    Room_category,
    Room_view,
    SiteSettings,
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

# name, room name, price (BDT), items, image, description,
# valid from, valid to, terms (one per line)
PACKAGES = [
    (
        "Weekend Getaway",
        "Family Suite",
        32000,
        ["Complimentary Breakfast", "Swimming Pool", "Guided City Tour"],
        "image_1.jpg",
        "A relaxing weekend for the whole family: breakfast each morning, "
        "pool access and a guided tour of the city on Saturday.",
        date(2026, 11, 23),
        date(2027, 3, 31),
        "Valid for stays of up to 3 nights\n"
        "Cannot be combined with other offers\n"
        "Free cancellation at any time",
    ),
    (
        "Honeymoon Special",
        "Premium Suite",
        45000,
        ["Complimentary Breakfast", "Spa Access", "Airport Pickup"],
        "image_2.jpg",
        "A romantic escape in our finest suite: breakfast in bed, a spa "
        "session for two and airport pickup on arrival.",
        date(2026, 11, 23),
        date(2027, 5, 31),
        "Valid for stays of up to 5 nights\n"
        "Spa session must be booked at least 24 hours ahead\n"
        "Free cancellation at any time",
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

BLOG_POSTS = [
    (
        "slow-morning-at-deluxe",
        "A slow morning at Deluxe: garden breakfasts and the outdoor pool",
        "hotel",
        "There is no better way to start a day here than breakfast by the garden, then a slow hour at the outdoor pool.",
        "Mornings at Deluxe move at their own pace. The garden-facing rooms catch the first light, and from the balcony you can hear the pool before you see it. Breakfast is served in the restaurant, and on a clear day the garden tables are the ones to ask for.\n\nAfter breakfast, the outdoor pool is at its quietest. Families tend to arrive later in the day, so the early hours belong to swimmers and readers. The kids' area opens with the pool, and the Family Suite is a two-minute walk away, which makes the morning routine easy when you are travelling with children.\n\nIf you are staying in a garden-view room, ask the front desk for a late check-out when you arrive. Check-out is at noon, but when the next guest arrives later in the day we are often able to stretch it — and a slow morning deserves a slow ending.",
        "images/image_1.jpg",
    ),
    (
        "planning-a-family-weekend",
        "Planning a family weekend: which room to pick and what to pack",
        "guide",
        "Two adults, two children, one weekend. Here is how to choose the room and pack the bag so the trip runs itself.",
        "The room is the decision that shapes the whole weekend. For a family of four, the Family Suite sleeps everyone comfortably with two queen beds, and the garden-facing balcony gives the adults somewhere to sit once the children are asleep. Every room has free Wi-Fi, air conditioning and a mini fridge — the fridge matters more than you think when you are travelling with small children.\n\nPack light, but pack for the pool: swimwear, sunscreen and a change of clothes for the journey home. The hotel provides towels at the pool, and daily housekeeping keeps the room reset while you are out. If you need anything during your stay, the front desk is the fastest way to get it.\n\nOne practical note: room bookings can be cancelled free of charge until two days before check-in, so if the children's plans change, yours can too. Book direct on this site and you can pay at the hotel — no card payment is needed in advance.",
        "images/image_2.jpg",
    ),
    (
        "winter-escape",
        "Winter escape: why the cooler months are the best time to stay",
        "guide",
        "Cooler air, quieter gardens and the best packages of the year. The winter season runs through March — here is how to make the most of it.",
        "The cooler months change the whole feel of the hotel. The gardens are at their greenest, the pool is warm in the afternoon sun, and the evenings are made for the balcony. It is also the season when our holiday packages run: the Weekend Getaway and the Honeymoon Special are both valid through the spring, and they bundle the room with the extras that make a short stay feel complete.\n\nA winter weekend works best with a loose plan. Arrive on Friday, settle in, and let Saturday shape itself around the pool and the restaurant. If you want a table for dinner, book it when you check in — weekends fill up.\n\nTravelling in the cooler months has one more advantage: the rooms with garden and pool views are easier to get. Book a little ahead, and you can pick the view you want rather than the one that is left.",
        "images/image_3.jpg",
    ),
    (
        "dinner-at-the-hotel",
        "Dinner at the hotel: what to expect from our restaurant",
        "dining",
        "A relaxed dining room, a menu that changes with the season, and tables for families as well as couples.",
        "Dinner at the hotel is deliberately unhurried. The dining room serves through the evening, the menu changes with the season, and there is always something straightforward for children alongside the main dishes. If you are staying with family, the early tables are the easiest — and the staff are used to high chairs and small appetites.\n\nCouples tend to come later, when the room quiets down. Ask for a garden-side table if you would like one; they are first come, first served.\n\nYou do not need to be a guest to eat with us, but guests get the simplest deal: charge dinner to the room and settle everything together at check-out. If you would like a table on a Friday or Saturday evening, it is worth asking at the front desk when you arrive.",
        "images/menu-1.jpg",
    ),
]


# Demo accounts shown on the login page so visitors can try the site.
# username, email, display name, is_staff, is_superuser
DEMO_USERS = [
    ("admin", "admin@demo.hotel", "Demo Admin", True, True),
    ("staff", "staff@demo.hotel", "Demo Staff", True, False),
    ("guest", "guest@demo.hotel", "Demo Guest", False, False),
]


# (slug, title, category, days_from_today, duration_days, time, location,
#  excerpt, body, image). Dates are relative to seeding day so the demo
# events are always upcoming when the demo data is seeded.
# Home-page hero slides: (heading, subheading, theme image file, order).
HERO_SLIDES = [
    ("Welcome To Deluxe", "Hotels & Resorts", "bg_1.jpg", 0),
    ("Enjoy A Luxury Experience", "Join With Us", "bg_2.jpg", 1),
]

EVENTS = [
    (
        "garden-dinner-under-the-stars",
        "Garden dinner under the stars",
        "dining",
        12,
        1,
        "7:00 PM – 10:00 PM",
        "The Garden",
        "A four-course dinner served at long tables in the garden, with the restaurant's seasonal menu and candles after dark.",
        "Once a month the restaurant moves outside. The kitchen serves a four-course seasonal menu at long tables in the garden, and the evening ends with dessert under the stars.\n\nTables seat eight and are shared between guests, so it is a good night to meet the people staying next door. Book a table at the front desk or through the restaurant page — the garden seats fill up first.",
        "images/menu-1.jpg",
    ),
    (
        "live-music-friday",
        "Live music Friday",
        "music",
        19,
        1,
        "8:00 PM – 11:00 PM",
        "The Lounge",
        "An evening of acoustic music in the lounge — no tickets, just turn up and order a drink.",
        "Every few weeks a local acoustic act plays in the lounge. There are no tickets and no reserved seats: come down after dinner, order a drink, and stay as long as you like.\n\nThe lounge keeps serving until 11:00 PM on music nights. If you prefer a quieter evening, the garden rooms face away from the lounge and stay peaceful.",
        "images/image_1.jpg",
    ),
    (
        "family-fun-weekend",
        "Family fun weekend",
        "family",
        26,
        2,
        "10:00 AM – 4:00 PM",
        "Poolside and kids' area",
        "Two days of games, pool activities and a kids' cooking session — free for families staying at the hotel.",
        "A weekend built around the kids' area and the pool: games on the lawn in the morning, pool activities after lunch, and a short cooking session for children on the second day.\n\nEverything is free for families staying at the hotel. Children stay with their parents throughout, and the front desk has the full schedule when you arrive.",
        "images/image_1.jpg",
    ),
    (
        "winter-tea-afternoon",
        "Winter tea afternoon",
        "seasonal",
        33,
        1,
        "3:00 PM – 5:00 PM",
        "The Restaurant",
        "Afternoon tea with seasonal bakes, served in the restaurant as the days get shorter.",
        "As the days get shorter we bring back the winter tea: a pot of tea or coffee, seasonal bakes from the kitchen, and a quiet table in the restaurant.\n\nNo booking needed — just come down between 3:00 PM and 5:00 PM. Guests can charge it to the room.",
        "images/menu-2.jpg",
    ),
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
        for (
            name,
            room_name,
            price,
            item_names,
            image,
            description,
            valid_from,
            valid_to,
            terms,
        ) in PACKAGES:
            package, _created = Package.objects.get_or_create(
                name=name,
                defaults={"room": rooms[room_name], "price": price},
            )
            # Set on every run so packages seeded before these fields
            # existed still get them.
            package.description = description
            package.valid_from = valid_from
            package.valid_to = valid_to
            package.terms = terms
            package.save()
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

        for slug, title, category, excerpt, body, image in BLOG_POSTS:
            BlogPost.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "category": category,
                    "excerpt": excerpt,
                    "body": body,
                    "image": image,
                },
            )
            self.stdout.write(f"Blog post: {title}")

        for (
            slug,
            title,
            category,
            days_out,
            duration,
            time_text,
            location,
            excerpt,
            body,
            image,
        ) in EVENTS:
            start = date.today() + timedelta(days=days_out)
            end = start + timedelta(days=duration - 1) if duration > 1 else None
            Event.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "category": category,
                    "start_date": start,
                    "end_date": end,
                    "time_text": time_text,
                    "location_text": location,
                    "excerpt": excerpt,
                    "body": body,
                    "image": image,
                },
            )
            self.stdout.write(f"Event: {title}")

        # Site information: one row, editable in the admin. Created only
        # when missing, so an admin's edits are never overwritten by a
        # later deploy's seed run.
        SiteSettings.objects.get_or_create(
            defaults={
                "hotel_name": "Deluxe",
                "address": (
                    "203 Fake St. Mountain View, San Francisco, "
                    "California, USA"
                ),
                "phone": "+2 392 3929 210",
                "email": "info@yourdomain.com",
                "check_in_time": "2:00 PM",
                "check_out_time": "12:00 PM",
            }
        )
        self.stdout.write("Site information: Deluxe")

        # Hero slideshow: the two theme slides, as admin-editable rows.
        # The image is (re-)copied only while the slide still uses the
        # seeded file — on every Vercel build media/ starts empty, so the
        # file must be restored, but a slide whose image was replaced in
        # the admin is left alone.
        for heading, subheading, image_file, order in HERO_SLIDES:
            slide, _created = HeroSlide.objects.get_or_create(
                heading=heading,
                defaults={"subheading": subheading, "order": order},
            )
            expected = f"hero/{image_file}"
            if not slide.image or slide.image.name == expected:
                self._ensure_image(slide.image, image_file)
            self.stdout.write(f"Hero slide: {heading}")

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
