import logging

import stripe
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date, timedelta
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView
from .models import Room, Package, Booking, Room_category, Package_Booking, Review
from django.db.models import Q, Avg
from .form import BookingForm, PackageBookingForm, ContactForm, ChangeDatesForm, ReviewForm
from .emails import (
    send_booking_confirmation,
    send_package_booking_confirmation,
    send_booking_cancellation,
    send_package_booking_cancellation,
    send_booking_dates_changed,
)
from .payments import (
    stripe_configured,
    create_checkout_session,
    mark_booking_paid,
    stripe_get,
)

logger = logging.getLogger(__name__)
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from sslcommerz_lib import SSLCOMMERZ
from decimal import Decimal
from django.views.generic import FormView
from django.urls import reverse_lazy
# Create your views here.


class HomeTemplate(TemplateView):
    all_rooms = Room.objects.all().filter(active=True)[:3]
    template_name = "hotelbooking/index.html"
    extra_context = {"rooms": all_rooms}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["testimonials"] = (
            Review.objects.select_related("room")
            .order_by("-created_at", "-id")[:5]
        )
        return context


class RoomsTemplate(View):
    def get(self, request):
        today = date.today()

        # Calculate tomorrow's date
        tomorrow = today + timedelta(days=1)

        # Get a list of all booked rooms for today and tomorrow
        booked_rooms = Booking.objects.filter(
            start_date__lte=today,
            end_date__gt=today,
            status=Booking.STATUS_CONFIRMED,
        ) | Booking.objects.filter(
            start_date__lt=tomorrow,
            end_date__gte=tomorrow,
            status=Booking.STATUS_CONFIRMED,
        )

        # Get a list of all rooms that are not booked today or tomorrow
        id_list = []
        for i in booked_rooms:
            id_list.append(i.room.id)
        available_rooms = Room.objects.exclude(id__in=id_list).filter(active=True)
        all_rooms = Room.objects.all().filter(active=True)
        template_name = "hotelbooking/rooms.html"
        context = {"rooms": available_rooms, "all_rooms": all_rooms}
        return render(request, template_name, context)

    def post(self, request):
        template_name = "hotelbooking/rooms.html"
        context = {}
        try:
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")
            room_type = request.POST.get("room_type")
            print("coming here...", start_date, end_date)
            
            if start_date and end_date:
            # Get rooms that are not booked during the requested period
                unavailable_rooms = Booking.objects.filter(
                    Q(start_date__lt=end_date) & Q(end_date__gt=start_date),
                    status=Booking.STATUS_CONFIRMED,
                ).values_list('room_id', flat=True)

                available_rooms = Room.objects.exclude(id__in=unavailable_rooms)
                try:
                    nights = (
                        datetime.strptime(end_date, "%Y-%m-%d").date()
                        - datetime.strptime(start_date, "%Y-%m-%d").date()
                    ).days
                except ValueError:
                    nights = None
                if nights is not None and nights < 1:
                    nights = None
                if nights:
                    for room in available_rooms:
                        room.stay_total = room.room_price * nights
                context = {
                    "rooms": available_rooms,
                    "start_date": start_date,
                    "end_date": end_date,
                    "nights": nights,
                }
                return render(request, 'hotelbooking/searchroom.html', context)
        except:
            return render(request, template_name)


class PackageTemplate(ListView):
    template_name = "hotelbooking/package.html"
    context_object_name = "packages"
    queryset = Package.objects.all().filter(active=True)


class RoomDetails(LoginRequiredMixin, TemplateView):

    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        try:
            if request.GET:
                if request.GET.get("choice") == "booking":
                    return redirect(f"/booking-room/{pk}")
                elif request.GET.get("choice") == "confirm_booking":
                    settings = {
                        "store_id": "adfa6429b57187712",
                        "store_pass": "adfa6429b57187712@ssl",
                        "issandbox": True,
                    }
                    sslcz = SSLCOMMERZ(settings)
                    post_body = {}
                    post_body["total_amount"] = room.room_price
                    post_body["currency"] = "BDT"
                    post_body["tran_id"] = "12345"
                    post_body["success_url"] = ""
                    post_body["fail_url"] = "your fail url"
                    post_body["cancel_url"] = "your cancel url"
                    post_body["emi_option"] = 0
                    post_body["cus_name"] = "test"
                    post_body["cus_email"] = "test@test.com"
                    post_body["cus_phone"] = "01700000000"
                    post_body["cus_add1"] = "customer address"
                    post_body["cus_city"] = "Dhaka"
                    post_body["cus_country"] = "Bangladesh"
                    post_body["shipping_method"] = "NO"
                    post_body["multi_card_name"] = ""
                    post_body["num_of_item"] = 1
                    post_body["product_name"] = "Test"
                    post_body["product_category"] = "Test Category"
                    post_body["product_profile"] = "general"
                    response = sslcz.createSession(post_body)
                    print(response)
                    return redirect(f"{response['GatewayPageURL']}")
                else:
                    pass

        except:
            pass

        room = Room.objects.get(id=pk)
        template_name = "hotelbooking/rooms-single.html"
        reviews = room.reviews.select_related("user").order_by("-created_at")
        average = reviews.aggregate(Avg("rating"))["rating__avg"]
        user_review = None
        if request.user.is_authenticated:
            user_review = reviews.filter(user=request.user).first()
        context = {
            "room": room,
            "reviews": reviews,
            "review_count": reviews.count(),
            "average_rating": round(average, 1) if average else None,
            "review_form": ReviewForm(instance=user_review),
            "user_review": user_review,
        }
        return render(request, template_name, context)


class AddReviewView(LoginRequiredMixin, View):
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        user_review = Review.objects.filter(
            room=room, user=request.user
        ).first()
        form = ReviewForm(request.POST, instance=user_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.room = room
            review.user = request.user
            review.guest_name = request.user.username
            review.save()
            if user_review:
                messages.success(request, "Your review has been updated.")
            else:
                messages.success(request, "Thank you for your review!")
        else:
            messages.error(
                request, "Please choose a rating and write your review."
            )
        return redirect("hotelbooking:details-room", pk=pk)


class DeleteReviewView(LoginRequiredMixin, View):
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        if review.user != request.user and not request.user.is_staff:
            raise Http404("Review not found")
        room_pk = review.room.pk
        review.delete()
        messages.success(request, "Your review has been deleted.")
        return redirect("hotelbooking:details-room", pk=room_pk)


class PoliciesFaqView(TemplateView):
    template_name = "hotelbooking/policies_faq.html"


class CreateBookingRoom(LoginRequiredMixin, View):
    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        form = BookingForm()
        template_name = "hotelbooking/createBooking.html"
        context = {"form": form, "id": pk, "room": room}
        return render(request, template_name, context)

    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        form = BookingForm(request.POST, instance=Booking(room=room))
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            send_booking_confirmation(booking)
            nights = (
                form.cleaned_data["end_date"] - form.cleaned_data["start_date"]
            ).days
            total = room.room_price * nights
            messages.success(
                request,
                f"Your booking for {room.room_name} is confirmed for "
                f"{form.cleaned_data['start_date']} to "
                f"{form.cleaned_data['end_date']} ({nights} night"
                f"{'s' if nights != 1 else ''}, total ${total}). "
                f"Your booking reference is {booking.reference}. "
                "Our team will call you for confirmation.",
            )
            return redirect("hotelbooking:rooms")
        template_name = "hotelbooking/createBooking.html"
        context = {"form": form, "id": pk, "room": room}
        return render(request, template_name, context)


class PackageBookingCreateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        package = Package.objects.get(id=pk)
        form = PackageBookingForm()
        template_name = "hotelbooking/create_package_booking.html"
        context = {"form": form, "id": pk, "package": package}
        return render(request, template_name, context)

    def post(self, request, pk):
        package = Package.objects.get(id=pk)
        form = PackageBookingForm(
            request.POST, instance=Package_Booking(package=package)
        )
        if form.is_valid():
            package_booking = form.save(commit=False)
            package_booking.user = request.user
            package_booking.save()
            send_package_booking_confirmation(package_booking)
            messages.success(
                request,
                f"Your booking for the {package.name} package is confirmed. "
                f"Your booking reference is {package_booking.reference}. "
                "Our team will call you for confirmation.",
            )
            return redirect("hotelbooking:packages")
        template_name = "hotelbooking/create_package_booking.html"
        context = {"form": form, "id": pk, "package": package}
        return render(request, template_name, context)


class MyBookingsView(LoginRequiredMixin, TemplateView):
    template_name = "hotelbooking/my_bookings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_bookings = (
            Booking.objects.filter(user=self.request.user)
            .select_related("room")
            .order_by("-created_at")
        )
        for booking in room_bookings:
            booking.nights = (booking.end_date - booking.start_date).days
            booking.stay_total = booking.room.room_price * booking.nights
        package_bookings = (
            Package_Booking.objects.filter(user=self.request.user)
            .select_related("package")
            .order_by("-created_at")
        )
        context["room_bookings"] = room_bookings
        context["package_bookings"] = package_bookings
        context["stripe_configured"] = stripe_configured()
        return context


class PayNowView(LoginRequiredMixin, View):
    def post(self, request, kind, reference):
        if kind not in ("room", "package"):
            raise Http404("Unknown booking type")
        if not stripe_configured():
            messages.error(request, "Online payment is not set up yet.")
            return redirect("hotelbooking:my-bookings")
        model = Booking if kind == "room" else Package_Booking
        booking = get_object_or_404(model, reference=reference, user=request.user)
        if booking.status != model.STATUS_CONFIRMED:
            messages.error(request, "Only confirmed bookings can be paid.")
            return redirect("hotelbooking:my-bookings")
        if booking.payment_status == model.PAYMENT_PAID:
            messages.info(
                request, f"Booking {booking.reference} is already paid."
            )
            return redirect("hotelbooking:my-bookings")
        try:
            session = create_checkout_session(request, booking, kind)
        except Exception:
            logger.exception("Stripe Checkout failed for %s", booking.reference)
            messages.error(
                request, "Could not start the payment. Please try again."
            )
            return redirect("hotelbooking:my-bookings")
        if not getattr(session, "url", None):
            messages.error(
                request, "Could not start the payment. Please try again."
            )
            return redirect("hotelbooking:my-bookings")
        return redirect(session.url)


class PaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        session_id = request.GET.get("session_id")
        if session_id and stripe_configured():
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                session = stripe.checkout.Session.retrieve(session_id)
                if session.payment_status == "paid":
                    booking = mark_booking_paid(session)
                    if booking:
                        messages.success(
                            request,
                            f"Payment received for booking "
                            f"{booking.reference}. Thank you!",
                        )
                        return redirect("hotelbooking:my-bookings")
            except Exception:
                logger.exception("Payment success check failed")
        messages.info(
            request,
            "Thanks for your payment. If it was completed, your booking "
            "will show as paid shortly.",
        )
        return redirect("hotelbooking:my-bookings")


class PaymentCancelView(LoginRequiredMixin, View):
    def get(self, request):
        messages.info(
            request,
            "Payment cancelled. Your booking is still confirmed — you can "
            "pay any time from My Bookings.",
        )
        return redirect("hotelbooking:my-bookings")


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request):
        if not settings.STRIPE_WEBHOOK_SECRET:
            return HttpResponseBadRequest("webhook not configured")
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return HttpResponseBadRequest("invalid signature")
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            if stripe_get(session, "payment_status") == "paid":
                mark_booking_paid(session)
        return HttpResponse(status=200)


class CancelRoomBookingView(LoginRequiredMixin, View):
    def get(self, request, reference):
        booking = get_object_or_404(
            Booking, reference=reference, user=request.user
        )
        if booking.status == Booking.STATUS_CANCELLED:
            messages.info(
                request, f"Booking {booking.reference} is already cancelled."
            )
            return redirect("hotelbooking:my-bookings")
        if booking.start_date - date.today() < timedelta(days=2):
            messages.error(
                request,
                "This booking can no longer be cancelled online. Free "
                "cancellation ends 2 days before check-in — please contact us.",
            )
            return redirect("hotelbooking:my-bookings")
        booking.nights = (booking.end_date - booking.start_date).days
        booking.stay_total = booking.room.room_price * booking.nights
        template_name = "hotelbooking/confirm_cancel.html"
        context = {"booking": booking, "kind": "room"}
        return render(request, template_name, context)

    def post(self, request, reference):
        booking = get_object_or_404(
            Booking, reference=reference, user=request.user
        )
        if booking.status == Booking.STATUS_CANCELLED:
            messages.info(
                request, f"Booking {booking.reference} is already cancelled."
            )
        elif booking.start_date - date.today() < timedelta(days=2):
            messages.error(
                request,
                "This booking can no longer be cancelled online. Free "
                "cancellation ends 2 days before check-in — please contact us.",
            )
        else:
            booking.status = Booking.STATUS_CANCELLED
            booking.save()
            send_booking_cancellation(booking)
            messages.success(
                request, f"Booking {booking.reference} has been cancelled."
            )
        return redirect("hotelbooking:my-bookings")


class CancelPackageBookingView(LoginRequiredMixin, View):
    def get(self, request, reference):
        booking = get_object_or_404(
            Package_Booking, reference=reference, user=request.user
        )
        if booking.status == Package_Booking.STATUS_CANCELLED:
            messages.info(
                request, f"Booking {booking.reference} is already cancelled."
            )
            return redirect("hotelbooking:my-bookings")
        template_name = "hotelbooking/confirm_cancel.html"
        context = {"booking": booking, "kind": "package"}
        return render(request, template_name, context)

    def post(self, request, reference):
        booking = get_object_or_404(
            Package_Booking, reference=reference, user=request.user
        )
        if booking.status == Package_Booking.STATUS_CANCELLED:
            messages.info(
                request, f"Booking {booking.reference} is already cancelled."
            )
        else:
            booking.status = Package_Booking.STATUS_CANCELLED
            booking.save()
            send_package_booking_cancellation(booking)
            messages.success(
                request, f"Booking {booking.reference} has been cancelled."
            )
        return redirect("hotelbooking:my-bookings")


class ChangeBookingDatesView(LoginRequiredMixin, View):
    def get(self, request, reference):
        booking = get_object_or_404(
            Booking, reference=reference, user=request.user
        )
        if booking.status != Booking.STATUS_CONFIRMED:
            messages.error(request, "Only confirmed bookings can be changed.")
            return redirect("hotelbooking:my-bookings")
        if booking.start_date <= date.today():
            messages.error(request, "This stay has already started.")
            return redirect("hotelbooking:my-bookings")
        form = ChangeDatesForm(instance=booking)
        template_name = "hotelbooking/change_dates.html"
        context = {"form": form, "booking": booking}
        return render(request, template_name, context)

    def post(self, request, reference):
        booking = get_object_or_404(
            Booking, reference=reference, user=request.user
        )
        if booking.status != Booking.STATUS_CONFIRMED:
            messages.error(request, "Only confirmed bookings can be changed.")
            return redirect("hotelbooking:my-bookings")
        if booking.start_date <= date.today():
            messages.error(request, "This stay has already started.")
            return redirect("hotelbooking:my-bookings")
        form = ChangeDatesForm(request.POST, instance=booking)
        if form.is_valid():
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            clash = (
                Booking.objects.filter(
                    room=booking.room,
                    status=Booking.STATUS_CONFIRMED,
                    start_date__lt=end_date,
                    end_date__gt=start_date,
                )
                .exclude(pk=booking.pk)
                .exists()
            )
            if clash:
                form.add_error(None, "This room is not available for those dates.")
            else:
                form.save()
                send_booking_dates_changed(booking)
                nights = (end_date - start_date).days
                total = booking.room.room_price * nights
                messages.success(
                    request,
                    f"Booking {booking.reference} moved to {start_date} - "
                    f"{end_date} ({nights} night"
                    f"{'s' if nights != 1 else ''}, total ${total}).",
                )
                return redirect("hotelbooking:my-bookings")
        template_name = "hotelbooking/change_dates.html"
        context = {"form": form, "booking": booking}
        return render(request, template_name, context)


class RestaurantsTemplateView(TemplateView):
    template_name = "hotelbooking/restaurants/main.html"
    

class AboutUsTemplateView(TemplateView):
    template_name = "hotelbooking/about/main.html"
    

class BlogTemplateView(TemplateView):
    template_name = "hotelbooking/blog/main.html"
    

class ContactFormView(FormView):
    form_class = ContactForm
    template_name = "hotelbooking/contact/main.html"
    success_url = reverse_lazy('hotelbooking:home')  # Redirect after a successful form submission

    def form_valid(self, form):
        # Save the form data to the database
        form.save()
        return super().form_valid(form)

    