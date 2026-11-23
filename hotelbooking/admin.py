from django.contrib import admin
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
    list_display = ("reference", "guest_name", "room", "start_date", "end_date", "status", "payment_status", "payment_method", "email", "user")
    list_filter = ("created_at", "status", "payment_status")
    search_fields = ["guest_name", "phone_number", "reference"]


@admin.register(Package_Booking)
class PackageBookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "name", "package", "phone_number", "status", "payment_status", "payment_method", "email", "user")
    list_filter = ("status", "payment_status")
    search_fields = ["name", "phone_number", "reference"]


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
    search_fields = ["name", "email", "message"]


@admin.register(Contact)
class LeadAdmin(admin.ModelAdmin):
    pass



admin.site.register(Room_category, Room_categoryAdmin)
admin.site.register(Package_item)
