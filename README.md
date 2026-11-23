# Hotel Booking App (Django)

A hotel booking website built with Django: browse rooms and packages,
search by date, and book a stay — as a guest or as a signed-in member.
Includes a restaurant page with table booking, a blog and events
calendar, on-site reviews, Stripe Checkout, and a hotel admin panel
with a reservation calendar.

**Live demo:** https://hotel-booking-app-django-1xzm.vercel.app/

## Features

### Booking

- Rooms with categories, views, photos, prices, capacity, bed and
  bathroom type, amenities and what's included
- Holiday packages with descriptions, validity dates and terms
- Date search showing only rooms free for the requested stay, filtered
  by room type and number of guests
- Guest checkout — no account needed; the booking is looked up later
  by reference and email on the Find Booking page
- Per-stay total price (nightly rate × nights), shown in search
  results, on the booking form and in the confirmation
- My Bookings page with `HB-XXXXXX` references; cancellation (free
  until 2 days before check-in) and date changes, with the same
  options for guests via Find Booking
- Member rate: signed-in members pay 10% less on room stays, plus
  late check-out until 1 PM and a free room upgrade when available
- Stripe Checkout (test mode) or pay at the hotel

### Content

- Home-page hero slideshow, managed in the admin (see below)
- Restaurant page with opening times, a sample menu and a Book a
  Table form (lunch and dinner slots)
- Blog with real posts, and an events calendar with upcoming hotel
  events grouped by month
- What's Included page, About page and a Policies & FAQ page
  (cancellation, payment, check-in 2:00 PM, check-out 12:00 PM)
- On-site reviews: guests rate and review rooms; the home page shows
  the newest real reviews
- Contact form plus a group / wedding / event enquiry form

### Email

- Booking, cancellation and date-change confirmations by email
  (SMTP when configured, console backend otherwise)

### Admin panel

- Reservation calendar: one row per room, one column per day —
  confirmed, cancelled and double-booked days at a glance
- Booking workflow: mark paid/unpaid, confirm (skips clashing
  bookings) and cancel, for room and package bookings
- Leads (group enquiries) and table bookings with status workflow
- Site information and hero slides (see below)
- Jazzmin-themed Django admin; CKEditor rich-text editing for room
  descriptions

## Admin-managed content

### Site information

Admin → Hotelbooking → Site information holds the hotel's public
details in a single row: hotel name, address, phone, email, and
check-in / check-out times. The footer contact block, the navbar
brand and the times on the Policies page all read from this row, so
editing it updates the whole site at once. Only one row can exist.

### Hero slideshow

Admin → Hotelbooking → Hero slides manages the home-page slideshow.
Each slide has a heading, a subheading, an image, an order number
and an active flag. Slides show in order, lowest first; untick
Active to hide a slide without deleting it.

**Image size:** upload wide landscape photos, **1920 × 1080 pixels
(16:9) or larger**. The slider stretches each image across the full
screen width, so portrait photos are heavily cropped and text near
the edges may be cut off. JPG or PNG, ideally under 500 KB so the
home page stays fast.

If no slide has a usable image, the home page falls back to the two
built-in theme slides, so the hero is never empty.

> Note: on the Vercel demo, files uploaded in the admin live on the
> host's ephemeral filesystem — they do not survive the next
> deployment. The seeded slides and room photos are re-created from
> the repository on every deploy, so the site always has images.

## Try the demo

No sign-up needed — the login page has one-click demo accounts
(all use the password `demo1234`):

| Role | Username | What it can do |
| --- | --- | --- |
| Admin (superuser) | `admin` | Full access, including the Django admin |
| Staff | `staff` | Manage bookings in the admin (no deleting, no user management) |
| Guest (user) | `guest` | Browse rooms and packages, make bookings |

Demo rooms, packages and accounts are re-seeded on every deployment,
so any demo data you change resets on the next deploy.

## Tech stack

- Python 3.12, Django 4.2
- PostgreSQL in production (Neon), SQLite locally
- django-allauth (authentication), django-ckeditor, django-jazzmin,
  django-crispy-forms (Bootstrap 4), Stripe (test-mode checkout)
- Hosted on Vercel (serverless); media files are served from the
  deployment

## Configuration

Environment variables (set in Vercel for the live demo):

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Yes | PostgreSQL connection string (Neon, direct, `?sslmode=require`) |
| `DJANGO_SECRET_KEY` | Yes | Django secret key |
| `DJANGO_DEBUG` | No | `False` in production |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_USE_TLS` | No | SMTP for real booking emails; without them, email goes to the console |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | No | Stripe test-mode keys; without them, checkout is disabled and bookings are pay-at-the-hotel |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Then open http://127.0.0.1:8000/ and sign in with a demo account above.

---

© 2026 Md Tanzil. All rights reserved.
