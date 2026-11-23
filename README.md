# Hotel Booking App (Django)

A hotel booking website built with Django: browse rooms and packages,
search by date, and book a stay. Includes a hotel admin panel, a
contact form, and rich-text room descriptions.

**Live demo:** https://hotel-booking-app-django-1xzm.vercel.app/

## Features

- Rooms with categories, views, photos, prices and capacity
- Packages bundling a room with extras (breakfast, spa, airport pickup)
- Date search showing only rooms free for the requested stay
- Room and package booking (sign-in required)
- Contact form, restaurant / about / blog pages
- Django admin with the Jazzmin theme
- CKEditor rich-text editing for room descriptions
- SSLCommerz payment stub (sandbox credentials, not a live checkout)

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
  django-crispy-forms (Bootstrap 4)
- WhiteNoise for media files, hosted on Vercel

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
