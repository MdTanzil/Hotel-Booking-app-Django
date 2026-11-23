from django.urls import path
from .views import (
    HomeTemplate,
    RoomsTemplate,
    PackageTemplate,
    RoomDetails,
    CreateBookingRoom,
    PackageBookingCreateView,
    MyBookingsView,
    RestaurantsTemplateView,
    AboutUsTemplateView,
    BlogTemplateView,
    ContactFormView
    
    
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
    path("my-bookings/", MyBookingsView.as_view(), name="my-bookings"),
    path('restaurants/', RestaurantsTemplateView.as_view(),name='restaurants_home'),
    path('about-us/', AboutUsTemplateView.as_view(),name='about-us'),
    path('blog/', BlogTemplateView.as_view(),name='blog'),
    path('contact/', ContactFormView.as_view(),name='contact-us'),
    
    
    
    
]
