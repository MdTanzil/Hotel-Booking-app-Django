import calendar as calendar_module
from datetime import date, timedelta

from django.contrib import admin, messages
from django.db.models import Q
from django.utils.html import format_html
from django.shortcuts import render
from django.urls import path
from .models import (
    Room_category,
    Room_view,
    Room,
    RoomAmenity,
    Package_item,
    Package,
    Booking,
    Package_Booking,
    Guest,
    Lead,
    Contact,
    Review,
    BlogPost,
    TableBooking,
    Event,
    SiteSettings,
    HeroSlide,
)


# Register your models here.
class Room_categoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "desc")


@admin.register(Room_view)
class Room_viewAdmin(admin.ModelAdmin):
    list_display = ("name", "desc")


@admin.register(RoomAmenity)
class RoomAmenityAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "room_name",
        "room_price",
        "max_person",
        "room_size",
        "room_category",
        "bed_type",
        "bathroom_type",
    )
    filter_horizontal = ("room_view", "amenities")


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("name", "room", "price", "valid_from", "valid_to")
    list_filter = ("valid_from", "valid_to")
    filter_horizontal = ("package_item",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "guest_name", "room", "start_date", "end_date", "status", "payment_status", "payment_method", "discount_rate", "email", "user")
    list_filter = ("created_at", "status", "payment_status")
    list_editable = ("status", "payment_status")
    date_hierarchy = "start_date"
    search_fields = ["guest_name", "phone_number", "reference"]
    actions = [
        "mark_paid",
        "mark_unpaid",
        "cancel_bookings",
        "confirm_bookings",
    ]
    change_list_template = "admin/hotelbooking/booking/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "calendar/",
                self.admin_site.admin_view(self.calendar_view),
                name="hotelbooking_booking_calendar",
            ),
        ]
        return custom + urls

    def calendar_view(self, request):
        """Month grid: one row per room, one column per day, bookings as
        coloured blocks. Cancelled bookings show greyed out; a red outline
        marks a day covered by more than one booking."""
        today = date.today()
        try:
            year = int(request.GET.get("year", today.year))
            month = int(request.GET.get("month", today.month))
            first_day = date(year, month, 1)
        except ValueError:
            first_day = date(today.year, today.month, 1)
            year, month = first_day.year, first_day.month
        days_in_month = calendar_module.monthrange(year, month)[1]
        last_day = date(year, month, days_in_month)
        prev_month = first_day - timedelta(days=1)
        next_month = last_day + timedelta(days=1)

        bookings = (
            Booking.objects.filter(
                start_date__lte=last_day,
                end_date__gt=first_day,
            )
            .select_related("room")
            .order_by("room__room_name", "start_date")
        )
        by_room = {}
        for booking in bookings:
            by_room.setdefault(booking.room_id, []).append(booking)

        rows = []
        for room in Room.objects.filter(active=True).order_by("room_name"):
            room_bookings = by_room.get(room.id, [])
            cells = []
            for day in range(1, days_in_month + 1):
                current = date(year, month, day)
                covering = [
                    b
                    for b in room_bookings
                    if b.start_date <= current < b.end_date
                ]
                if not covering:
                    cells.append(None)
                    continue
                booking = covering[0]
                cells.append(
                    {
                        "booking": booking,
                        "is_start": booking.start_date == current
                        or current == first_day,
                        "clash": len(covering) > 1,
                    }
                )
            rows.append({"room": room, "cells": cells})

        context = {
            **self.admin_site.each_context(request),
            "title": "Reservation calendar",
            "year": year,
            "month": month,
            "month_name": calendar_module.month_name[month],
            "days": list(range(1, days_in_month + 1)),
            "rows": rows,
            "prev_year": prev_month.year,
            "prev_month": prev_month.month,
            "next_year": next_month.year,
            "next_month": next_month.month,
            "opts": self.model._meta,
        }
        return render(
            request, "admin/hotelbooking/booking/calendar.html", context
        )

    @admin.action(description="Mark selected bookings as paid")
    def mark_paid(self, request, queryset):
        updated = queryset.update(payment_status=Booking.PAYMENT_PAID)
        self.message_user(
            request, f"{updated} booking(s) marked as paid.", messages.SUCCESS
        )

    @admin.action(description="Mark selected bookings as unpaid")
    def mark_unpaid(self, request, queryset):
        updated = queryset.update(payment_status=Booking.PAYMENT_UNPAID)
        self.message_user(
            request,
            f"{updated} booking(s) marked as unpaid.",
            messages.SUCCESS,
        )

    @admin.action(description="Cancel selected bookings")
    def cancel_bookings(self, request, queryset):
        updated = queryset.update(status=Booking.STATUS_CANCELLED)
        self.message_user(
            request, f"{updated} booking(s) cancelled.", messages.SUCCESS
        )

    @admin.action(description="Confirm selected bookings")
    def confirm_bookings(self, request, queryset):
        confirmed = 0
        skipped = 0
        for booking in queryset:
            clash = (
                Booking.objects.filter(
                    room=booking.room,
                    status=Booking.STATUS_CONFIRMED,
                    start_date__lt=booking.end_date,
                    end_date__gt=booking.start_date,
                )
                .exclude(pk=booking.pk)
                .exists()
            )
            if clash:
                skipped += 1
                continue
            booking.status = Booking.STATUS_CONFIRMED
            booking.save()
            confirmed += 1
        if confirmed:
            self.message_user(
                request,
                f"{confirmed} booking(s) confirmed.",
                messages.SUCCESS,
            )
        if skipped:
            self.message_user(
                request,
                f"{skipped} booking(s) skipped — another confirmed booking "
                "already covers those dates for the same room.",
                messages.WARNING,
            )


@admin.register(Package_Booking)
class PackageBookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "name", "package", "phone_number", "status", "payment_status", "payment_method", "email", "user")
    list_filter = ("status", "payment_status")
    list_editable = ("status", "payment_status")
    search_fields = ["name", "phone_number", "reference"]
    actions = [
        "mark_paid",
        "mark_unpaid",
        "cancel_bookings",
        "confirm_bookings",
    ]

    @admin.action(description="Mark selected package bookings as paid")
    def mark_paid(self, request, queryset):
        updated = queryset.update(payment_status=Package_Booking.PAYMENT_PAID)
        self.message_user(
            request, f"{updated} package booking(s) marked as paid.", messages.SUCCESS
        )

    @admin.action(description="Mark selected package bookings as unpaid")
    def mark_unpaid(self, request, queryset):
        updated = queryset.update(
            payment_status=Package_Booking.PAYMENT_UNPAID
        )
        self.message_user(
            request,
            f"{updated} package booking(s) marked as unpaid.",
            messages.SUCCESS,
        )

    @admin.action(description="Cancel selected package bookings")
    def cancel_bookings(self, request, queryset):
        updated = queryset.update(status=Package_Booking.STATUS_CANCELLED)
        self.message_user(
            request,
            f"{updated} package booking(s) cancelled.",
            messages.SUCCESS,
        )

    @admin.action(description="Confirm selected package bookings")
    def confirm_bookings(self, request, queryset):
        updated = queryset.update(status=Package_Booking.STATUS_CONFIRMED)
        self.message_user(
            request,
            f"{updated} package booking(s) confirmed.",
            messages.SUCCESS,
        )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("guest_name", "room", "rating", "created_at")
    list_filter = ("rating", "room")
    search_fields = ["guest_name", "text"]


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published", "created_at")
    list_filter = ("category", "published")
    search_fields = ["title", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date", "category", "published")
    list_filter = ("category", "published")
    search_fields = ["title", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Singleton: one row holds the hotel's public information.

    The footer contact block, the navbar brand and the check-in/out times
    on the Policies page read from this row, so editing here updates the
    whole site at once.
    """

    list_display = ("hotel_name", "phone", "email", "updated_at")
    fieldsets = (
        (None, {"fields": ("hotel_name",)}),
        ("Contact (shown in the footer)", {"fields": ("address", "phone", "email")}),
        (
            "Check-in / check-out (shown on the Policies page)",
            {"fields": ("check_in_time", "check_out_time")},
        ),
    )

    def has_add_permission(self, request):
        # Singleton: only one row may exist.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Deleting the only row would silently revert the site to defaults.
        return False


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    """Home-page hero slideshow: upload images, order them, hide/show."""

    list_display = ("preview", "heading", "order", "active", "updated_at")
    list_editable = ("order", "active")
    search_fields = ["heading", "subheading"]
    readonly_fields = ("preview_large",)
    fieldsets = (
        (
            None,
            {
                "fields": ("heading", "subheading", "image", "preview_large"),
                "description": (
                    "Images should be 1920 x 1080 pixels (16:9) or larger — "
                    "wide landscape photos. The slider stretches each image "
                    "across the full screen width."
                ),
            },
        ),
        ("Order & visibility", {"fields": ("order", "active")}),
    )

    def preview(self, obj):
        if not obj.image:
            return "—"
        return format_html(
            '<img src="{}" style="width:120px;height:auto;" alt="">',
            obj.image.url,
        )

    preview.short_description = "Image"

    def preview_large(self, obj):
        if not obj.image:
            return "No image uploaded yet."
        return format_html(
            '<img src="{}" style="max-width:600px;width:100%;height:auto;" alt="">',
            obj.image.url,
        )

    preview_large.short_description = "Preview"


@admin.register(TableBooking)
class TableBookingAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "time", "guests", "status", "created_at")
    list_filter = ("status", "date")
    list_editable = ("status",)
    search_fields = ["name", "email", "occasion"]
    actions = ["confirm_tables", "cancel_tables"]

    @admin.action(description="Confirm selected table bookings")
    def confirm_tables(self, request, queryset):
        updated = queryset.update(status=TableBooking.STATUS_CONFIRMED)
        self.message_user(
            request,
            f"{updated} table booking(s) confirmed.",
            messages.SUCCESS,
        )

    @admin.action(description="Cancel selected table bookings")
    def cancel_tables(self, request, queryset):
        updated = queryset.update(status=TableBooking.STATUS_CANCELLED)
        self.message_user(
            request,
            f"{updated} table booking(s) cancelled.",
            messages.SUCCESS,
        )


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ("guest_name", "phone_number", "nid_number", "permanent_address")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "event_type",
        "start_date",
        "end_date",
        "adult_member",
        "child",
        "rooms_needed",
        "status",
        "created_at",
    )
    list_filter = ("status", "event_type")
    list_editable = ("status",)
    date_hierarchy = "start_date"
    search_fields = ["name", "email", "message"]
    actions = ["mark_contacted", "mark_closed", "mark_new"]

    @admin.action(description="Mark selected leads as contacted")
    def mark_contacted(self, request, queryset):
        updated = queryset.update(status=Lead.STATUS_CONTACTED)
        self.message_user(
            request, f"{updated} lead(s) marked as contacted.", messages.SUCCESS
        )

    @admin.action(description="Mark selected leads as closed")
    def mark_closed(self, request, queryset):
        updated = queryset.update(status=Lead.STATUS_CLOSED)
        self.message_user(
            request, f"{updated} lead(s) marked as closed.", messages.SUCCESS
        )

    @admin.action(description="Reopen selected leads as new")
    def mark_new(self, request, queryset):
        updated = queryset.update(status=Lead.STATUS_NEW)
        self.message_user(
            request, f"{updated} lead(s) reopened as new.", messages.SUCCESS
        )


@admin.register(Contact)
class LeadAdmin(admin.ModelAdmin):
    pass



admin.site.register(Room_category, Room_categoryAdmin)
admin.site.register(Package_item)
