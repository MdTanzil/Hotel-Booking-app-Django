from django.urls import path
from .views import (
    HomeTemplate,
    RoomsTemplate,
    PackageTemplate,
    RoomDetails,
    CreateBookingRoom,
    PackageBookingCreateView,
    MyBookingsView,
    CancelRoomBookingView,
    CancelPackageBookingView,
    ChangeBookingDatesView,
    PayNowView,
    PaymentSuccessView,
    PaymentCancelView,
    StripeWebhookView,
    AddReviewView,
    DeleteReviewView,
    PoliciesFaqView,
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
    path(
        "details-room/<str:pk>/review/",
        AddReviewView.as_view(),
        name="add-review",
    ),
    path(
        "reviews/<int:pk>/delete/",
        DeleteReviewView.as_view(),
        name="delete-review",
    ),
    path("booking-room/<str:pk>", CreateBookingRoom.as_view(), name="booking-room"),
    path(
        "booking-package/<str:pk>",
        PackageBookingCreateView.as_view(),
        name="booking-package",
    ),
    path("my-bookings/", MyBookingsView.as_view(), name="my-bookings"),
    path(
        "my-bookings/cancel-room/<str:reference>/",
        CancelRoomBookingView.as_view(),
        name="cancel-room-booking",
    ),
    path(
        "my-bookings/cancel-package/<str:reference>/",
        CancelPackageBookingView.as_view(),
        name="cancel-package-booking",
    ),
    path(
        "my-bookings/change-dates/<str:reference>/",
        ChangeBookingDatesView.as_view(),
        name="change-booking-dates",
    ),
    path(
        "my-bookings/pay/<str:kind>/<str:reference>/",
        PayNowView.as_view(),
        name="pay-now",
    ),
    path(
        "my-bookings/payment/success/",
        PaymentSuccessView.as_view(),
        name="payment-success",
    ),
    path(
        "my-bookings/payment/cancelled/",
        PaymentCancelView.as_view(),
        name="payment-cancel",
    ),
    path("stripe-webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path('restaurants/', RestaurantsTemplateView.as_view(),name='restaurants_home'),
    path('about-us/', AboutUsTemplateView.as_view(),name='about-us'),
    path('blog/', BlogTemplateView.as_view(),name='blog'),
    path('policies/', PoliciesFaqView.as_view(), name='policies-faq'),
    path('contact/', ContactFormView.as_view(),name='contact-us'),
    
    
    
    
]
