from django.urls import path
from .views import (
    HomeTemplate,
    RoomsTemplate,
    PackageTemplate,
    RoomDetails,
    CreateBookingRoom,
    PackageBookingCreateView,
)

app_name = "hotelbooking"
urlpatterns = [
    path("", HomeTemplate.as_view(), name="home"),
    path("rooms/", RoomsTemplate.as_view(), name="rooms"),
    path("package/", PackageTemplate.as_view(), name="packages"),
    path("details-room/<str:pk>", RoomDetails.as_view(), name="details-room"),
    path("booking-room/<str:pk>", CreateBookingRoom.as_view(), name="booking-room"),
    path(
        "booking-package/<str:pk>",
        PackageBookingCreateView.as_view(),
        name="booking-package",
    ),
]
