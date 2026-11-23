from django.forms import ModelForm
from django import forms
from .models import Booking, Package_Booking, Contact, Review
from datetime import datetime

# Create the form class.


class BookingForm(ModelForm):
    guest_name = forms.CharField(required=True, label="Name")
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

    class Meta:
        model = Package_Booking
        exclude = ["package", "active", "user", "reference", "status", "payment_status"]


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

