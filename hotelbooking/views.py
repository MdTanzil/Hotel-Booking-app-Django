import logging

import stripe
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date, timedelta
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, DetailView
from .models import Room, Package, Booking, Room_category, Package_Booking, Review, BlogPost
from django.db.models import Q, Avg
from .form import BookingForm, PackageBookingForm, ContactForm, ChangeDatesForm, ReviewForm, FindBookingForm, LeadForm
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
        context["room_categories"] = Room_category.objects.all()
        context["adults"] = 2
        context["children"] = 0
        context["latest_posts"] = BlogPost.objects.filter(published=True)[:4]
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
        context = {
            "rooms": available_rooms,
            "all_rooms": all_rooms,
            "room_categories": Room_category.objects.all(),
            "adults": 2,
            "children": 0,
        }
        return render(request, template_name, context)

    def post(self, request):
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        if not start_date or not end_date:
            messages.error(
                request, "Please choose your check-in and check-out dates."
            )
            return redirect("hotelbooking:rooms")
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Please choose valid dates.")
            return redirect("hotelbooking:rooms")
        nights = (end - start).days
        if nights < 1:
            messages.error(
                request, "Check-out date must be after check-in date."
            )
            return redirect("hotelbooking:rooms")

        try:
            adults = max(1, min(6, int(request.POST.get("adults", 2))))
        except (TypeError, ValueError):
            adults = 2
        try:
            children = max(0, min(4, int(request.POST.get("children", 0))))
        except (TypeError, ValueError):
            children = 0
        guests = adults + children

        room_type = request.POST.get("room_type") or ""
        room_type_name = ""
        try:
            room_type_id = int(room_type) if room_type else None
        except ValueError:
            room_type_id = None
        if room_type_id:
            category = Room_category.objects.filter(pk=room_type_id).first()
            if category:
                room_type_name = category.name
            else:
                room_type_id = None

        # Rooms that are not booked during the requested period.
        unavailable_rooms = Booking.objects.filter(
            Q(start_date__lt=end_date) & Q(end_date__gt=start_date),
            status=Booking.STATUS_CONFIRMED,
        ).values_list("room_id", flat=True)
        available_rooms = Room.objects.exclude(id__in=unavailable_rooms).filter(
            active=True, max_person__gte=guests
        )
        if room_type_id:
            available_rooms = available_rooms.filter(
                room_category_id=room_type_id
            )
        for room in available_rooms:
            room.stay_total = room.room_price * nights
        context = {
            "rooms": available_rooms,
            "start_date": start_date,
            "end_date": end_date,
            "nights": nights,
            "adults": adults,
            "children": children,
            "room_type": room_type,
            "room_type_name": room_type_name,
            "room_categories": Room_category.objects.all(),
        }
        return render(request, "hotelbooking/searchroom.html", context)


class PackageTemplate(ListView):
    template_name = "hotelbooking/package.html"
    context_object_name = "packages"

    def get_queryset(self):
        today = date.today()
        return (
            Package.objects.filter(active=True)
            .filter(Q(valid_from__isnull=True) | Q(valid_from__lte=today))
            .filter(Q(valid_to__isnull=True) | Q(valid_to__gte=today))
        )


class RoomDetails(TemplateView):

    def get(self, request, pk):
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


class CreateBookingRoom(View):
    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        initial = {}
        if request.user.is_authenticated and request.user.email:
            initial["email"] = request.user.email
        form = BookingForm(
            initial=initial, stripe_available=stripe_configured()
        )
        template_name = "hotelbooking/createBooking.html"
        context = {"form": form, "id": pk, "room": room}
        return render(request, template_name, context)

    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        form = BookingForm(
            request.POST,
            instance=Booking(room=room),
            stripe_available=stripe_configured(),
        )
        if form.is_valid():
            booking = form.save(commit=False)
            if request.user.is_authenticated:
                booking.user = request.user
            booking.save()
            send_booking_confirmation(booking)
            nights = (
                form.cleaned_data["end_date"] - form.cleaned_data["start_date"]
            ).days
            total = room.room_price * nights
            if (
                booking.payment_method == Booking.PAY_ONLINE
                and stripe_configured()
            ):
                try:
                    session = create_checkout_session(
                        request, booking, "room"
                    )
                    if getattr(session, "url", None):
                        request.session["guest_booking_ref"] = booking.reference
                        return redirect(session.url)
                except Exception:
                    logger.exception(
                        "Stripe Checkout failed for %s", booking.reference
                    )
                messages.warning(
                    request,
                    "Your booking is confirmed, but online payment could "
                    "not be started — please pay at the hotel or try again "
                    "from My Bookings.",
                )
            else:
                messages.success(
                    request,
                    f"Your booking for {room.room_name} is confirmed for "
                    f"{form.cleaned_data['start_date']} to "
                    f"{form.cleaned_data['end_date']} ({nights} night"
                    f"{'s' if nights != 1 else ''}, total ${total}). "
                    f"Your booking reference is {booking.reference}. "
                    "Our team will call you for confirmation.",
                )
            if request.user.is_authenticated:
                return redirect("hotelbooking:rooms")
            request.session["guest_booking_ref"] = booking.reference
            return redirect(
                "hotelbooking:guest-booking-detail",
                reference=booking.reference,
            )
        template_name = "hotelbooking/createBooking.html"
        context = {"form": form, "id": pk, "room": room}
        return render(request, template_name, context)


class PackageBookingCreateView(View):
    def get(self, request, pk):
        package = Package.objects.get(id=pk)
        if not package.is_current:
            messages.error(
                request, "This package is no longer available."
            )
            return redirect("hotelbooking:packages")
        initial = {}
        if request.user.is_authenticated and request.user.email:
            initial["email"] = request.user.email
        form = PackageBookingForm(
            initial=initial, stripe_available=stripe_configured()
        )
        template_name = "hotelbooking/create_package_booking.html"
        context = {"form": form, "id": pk, "package": package}
        return render(request, template_name, context)

    def post(self, request, pk):
        package = Package.objects.get(id=pk)
        if not package.is_current:
            messages.error(
                request, "This package is no longer available."
            )
            return redirect("hotelbooking:packages")
        form = PackageBookingForm(
            request.POST,
            instance=Package_Booking(package=package),
            stripe_available=stripe_configured(),
        )
        if form.is_valid():
            package_booking = form.save(commit=False)
            if request.user.is_authenticated:
                package_booking.user = request.user
            package_booking.save()
            send_package_booking_confirmation(package_booking)
            if (
                package_booking.payment_method == Package_Booking.PAY_ONLINE
                and stripe_configured()
            ):
                try:
                    session = create_checkout_session(
                        request, package_booking, "package"
                    )
                    if getattr(session, "url", None):
                        request.session["guest_booking_ref"] = (
                            package_booking.reference
                        )
                        return redirect(session.url)
                except Exception:
                    logger.exception(
                        "Stripe Checkout failed for %s",
                        package_booking.reference,
                    )
                messages.warning(
                    request,
                    "Your booking is confirmed, but online payment could "
                    "not be started — please pay at the hotel or try again "
                    "from My Bookings.",
                )
            else:
                messages.success(
                    request,
                    f"Your booking for the {package.name} package is confirmed. "
                    f"Your booking reference is {package_booking.reference}. "
                    "Our team will call you for confirmation.",
                )
            if request.user.is_authenticated:
                return redirect("hotelbooking:packages")
            request.session["guest_booking_ref"] = package_booking.reference
            return redirect(
                "hotelbooking:guest-booking-detail",
                reference=package_booking.reference,
            )
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
    

class BlogTemplateView(ListView):
    model = BlogPost
    template_name = "hotelbooking/blog/main.html"
    context_object_name = "posts"

    def get_queryset(self):
        return BlogPost.objects.filter(published=True)


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = "hotelbooking/blog/detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return BlogPost.objects.filter(published=True)

class ContactFormView(View):
    template_name = "hotelbooking/contact/main.html"

    def get(self, request):
        context = {"form": ContactForm(), "lead_form": LeadForm()}
        return render(request, self.template_name, context)

    def post(self, request):
        if request.POST.get("form_kind") == "group":
            lead_form = LeadForm(request.POST)
            if lead_form.is_valid():
                lead_form.save()
                messages.success(
                    request,
                    "Thank you — your group enquiry has been received. "
                    "Our team will get back to you within one business day.",
                )
                return redirect("hotelbooking:contact-us")
            context = {"form": ContactForm(), "lead_form": lead_form}
            return render(request, self.template_name, context)
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thank you for your message. Our team will get back to you soon.",
            )
            return redirect("hotelbooking:home")
        context = {"form": form, "lead_form": LeadForm()}
        return render(request, self.template_name, context)

    

def _find_booking_by_reference(reference):
    """Return ("room", booking) or ("package", booking) for a reference,
    or (None, None) when nothing matches."""
    booking = Booking.objects.filter(reference=reference).first()
    if booking:
        return "room", booking
    booking = Package_Booking.objects.filter(reference=reference).first()
    if booking:
        return "package", booking
    return None, None


def _guest_can_access(request, booking):
    """A booking may be viewed when the visitor verified it through the
    find-my-booking lookup (session holds the reference), owns it, or is
    staff."""
    if request.session.get("guest_booking_ref") == booking.reference:
        return True
    if request.user.is_authenticated and (
        booking.user == request.user or request.user.is_staff
    ):
        return True
    return False


class FindBookingView(View):
    def get(self, request):
        form = FindBookingForm()
        return render(
            request, "hotelbooking/find_booking.html", {"form": form}
        )

    def post(self, request):
        form = FindBookingForm(request.POST)
        if form.is_valid():
            reference = form.cleaned_data["reference"].strip().upper()
            email = form.cleaned_data["email"].strip().lower()
            _kind, booking = _find_booking_by_reference(reference)
            if booking and booking.contact_email.lower() == email:
                request.session["guest_booking_ref"] = booking.reference
                return redirect(
                    "hotelbooking:guest-booking-detail",
                    reference=booking.reference,
                )
            messages.error(
                request,
                "No booking found with that reference and email. Please "
                "check both and try again.",
            )
        return render(
            request, "hotelbooking/find_booking.html", {"form": form}
        )


class GuestBookingDetailView(View):
    def get(self, request, reference):
        kind, booking = _find_booking_by_reference(reference)
        if not booking:
            raise Http404("Booking not found")
        if not _guest_can_access(request, booking):
            messages.error(
                request,
                "Please enter your booking reference and email to view "
                "this booking.",
            )
            return redirect("hotelbooking:find-booking")
        if kind == "room":
            booking.nights = (booking.end_date - booking.start_date).days
            booking.stay_total = booking.room.room_price * booking.nights
        context = {
            "booking": booking,
            "kind": kind,
            "stripe_configured": stripe_configured(),
        }
        return render(
            request, "hotelbooking/guest_booking_detail.html", context
        )


class GuestCancelBookingView(View):
    def get(self, request, reference):
        kind, booking = _find_booking_by_reference(reference)
        if not booking:
            raise Http404("Booking not found")
        if not _guest_can_access(request, booking):
            messages.error(
                request,
                "Please enter your booking reference and email to view "
                "this booking.",
            )
            return redirect("hotelbooking:find-booking")
        if booking.status == Booking.STATUS_CANCELLED:
            messages.info(
                request, f"Booking {booking.reference} is already cancelled."
            )
            return redirect(
                "hotelbooking:guest-booking-detail", reference=reference
            )
        if kind == "room" and booking.start_date - date.today() < timedelta(
            days=2
        ):
            messages.error(
                request,
                "This booking can no longer be cancelled online. Free "
                "cancellation ends 2 days before check-in — please contact us.",
            )
            return redirect(
                "hotelbooking:guest-booking-detail", reference=reference
            )
        if kind == "room":
            booking.nights = (booking.end_date - booking.start_date).days
            booking.stay_total = booking.room.room_price * booking.nights
        context = {
            "booking": booking,
            "kind": kind,
            "back_url": reverse(
                "hotelbooking:guest-booking-detail", args=[reference]
            ),
        }
        return render(request, "hotelbooking/confirm_cancel.html", context)

    def post(self, request, reference):
        kind, booking = _find_booking_by_reference(reference)
        if not booking:
            raise Http404("Booking not found")
        if not _guest_can_access(request, booking):
            messages.error(
                request,
                "Please enter your booking reference and email to view "
                "this booking.",
            )
            return redirect("hotelbooking:find-booking")
        if booking.status == Booking.STATUS_CANCELLED:
            messages.info(
                request, f"Booking {booking.reference} is already cancelled."
            )
        elif kind == "room" and booking.start_date - date.today() < timedelta(
            days=2
        ):
            messages.error(
                request,
                "This booking can no longer be cancelled online. Free "
                "cancellation ends 2 days before check-in — please contact us.",
            )
        else:
            booking.status = Booking.STATUS_CANCELLED
            booking.save()
            if kind == "room":
                send_booking_cancellation(booking)
            else:
                send_package_booking_cancellation(booking)
            messages.success(
                request, f"Booking {booking.reference} has been cancelled."
            )
        return redirect(
            "hotelbooking:guest-booking-detail", reference=reference
        )


class GuestPayView(View):
    def post(self, request, reference):
        kind, booking = _find_booking_by_reference(reference)
        if not booking:
            raise Http404("Booking not found")
        if not _guest_can_access(request, booking):
            messages.error(
                request,
                "Please enter your booking reference and email to view "
                "this booking.",
            )
            return redirect("hotelbooking:find-booking")
        if booking.status != Booking.STATUS_CONFIRMED:
            messages.error(request, "This booking cannot be paid.")
            return redirect(
                "hotelbooking:guest-booking-detail", reference=reference
            )
        if booking.payment_status == Booking.PAYMENT_PAID:
            messages.info(request, "This booking is already paid.")
            return redirect(
                "hotelbooking:guest-booking-detail", reference=reference
            )
        if not stripe_configured():
            messages.error(
                request,
                "Online payment is not set up yet — please pay at the hotel.",
            )
            return redirect(
                "hotelbooking:guest-booking-detail", reference=reference
            )
        try:
            session = create_checkout_session(request, booking, kind)
        except Exception:
            logger.exception("Stripe Checkout failed for %s", reference)
            messages.error(
                request, "Could not start the payment. Please try again."
            )
            return redirect(
                "hotelbooking:guest-booking-detail", reference=reference
            )
        if not getattr(session, "url", None):
            messages.error(
                request, "Could not start the payment. Please try again."
            )
            return redirect(
                "hotelbooking:guest-booking-detail", reference=reference
            )
        return redirect(session.url)
