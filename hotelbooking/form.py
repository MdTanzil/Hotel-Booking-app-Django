from django.forms import ModelForm
from django import forms
from .models import Booking, Package_Booking, Contact, Review, Lead
from datetime import datetime

# Create the form class.


class BookingForm(ModelForm):
    guest_name = forms.CharField(required=True, label="Name")
    email = forms.EmailField(
        required=True,
        label="Email",
        help_text="Your confirmation and booking reference will be sent here.",
    )
    start_date = forms.DateField(
        required=True,
        label="Check in Date",
        widget=forms.DateInput(attrs={"type": "date", "min": datetime.now().date()}),
    )
    end_date = forms.DateField(
        required=True,
        label="Check out Date",
        widget=forms.DateInput(attrs={"type": "date", "min": datetime.now().date()}),
    )
    payment_method = forms.ChoiceField(
        label="How would you like to pay?",
        choices=Booking.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        initial=Booking.PAY_AT_PROPERTY,
    )

    def __init__(self, *args, stripe_available=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not stripe_available:
            self.fields["payment_method"].choices = [
                (Booking.PAY_AT_PROPERTY, "Pay at the hotel")
            ]

    class Meta:
        model = Booking
        exclude = ["active", "room", "user", "reference", "status", "payment_status"]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and end_date <= start_date:
            self.add_error("end_date", "Check out date must be after check in date.")
        return cleaned_data


class PackageBookingForm(ModelForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        help_text="Your confirmation and booking reference will be sent here.",
    )
    payment_method = forms.ChoiceField(
        label="How would you like to pay?",
        choices=Package_Booking.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        initial=Package_Booking.PAY_AT_PROPERTY,
    )

    def __init__(self, *args, stripe_available=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not stripe_available:
            self.fields["payment_method"].choices = [
                (Package_Booking.PAY_AT_PROPERTY, "Pay at the hotel")
            ]

    class Meta:
        model = Package_Booking
        exclude = ["package", "active", "user", "reference", "status", "payment_status"]


class FindBookingForm(forms.Form):
    reference = forms.CharField(
        label="Booking reference",
        max_length=12,
        help_text="For example HB-XXXXXX — it was in your confirmation message.",
    )
    email = forms.EmailField(label="Email used for the booking")


class ChangeDatesForm(ModelForm):
    start_date = forms.DateField(
        required=True,
        label="New check in Date",
        widget=forms.DateInput(attrs={"type": "date", "min": datetime.now().date()}),
    )
    end_date = forms.DateField(
        required=True,
        label="New check out Date",
        widget=forms.DateInput(attrs={"type": "date", "min": datetime.now().date()}),
    )

    class Meta:
        model = Booking
        fields = ["start_date", "end_date"]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and end_date <= start_date:
            self.add_error("end_date", "Check out date must be after check in date.")
        return cleaned_data

class ContactForm(ModelForm):
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone_number', 'subject', 'message']


class ReviewForm(ModelForm):
    rating = forms.TypedChoiceField(
        choices=[
            (5, "5 - Excellent"),
            (4, "4 - Very good"),
            (3, "3 - Good"),
            (2, "2 - Fair"),
            (1, "1 - Poor"),
        ],
        coerce=int,
        widget=forms.RadioSelect,
    )
    text = forms.CharField(
        label="Your review",
        widget=forms.Textarea(attrs={"rows": 3, "maxlength": "1000"}),
    )

    class Meta:
        model = Review
        fields = ["rating", "text"]



class LeadForm(ModelForm):
    start_date = forms.DateField(
        required=True,
        label="Arrival date",
        widget=forms.DateInput(attrs={"type": "date", "min": datetime.now().date()}),
    )
    end_date = forms.DateField(
        required=True,
        label="Departure date",
        widget=forms.DateInput(attrs={"type": "date", "min": datetime.now().date()}),
    )
    message = forms.CharField(
        label="Tell us about your event",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Anything that helps us prepare a quote: occasion, schedule, dining or meeting needs.",
    )

    class Meta:
        model = Lead
        fields = [
            "name",
            "email",
            "phone_number",
            "event_type",
            "start_date",
            "end_date",
            "adult_member",
            "child",
            "rooms_needed",
            "message",
        ]
        labels = {
            "adult_member": "Adults",
            "child": "Children",
            "rooms_needed": "Rooms needed",
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and end_date <= start_date:
            self.add_error("end_date", "Departure date must be after arrival date.")
        return cleaned_data
