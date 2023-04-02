from django.forms import ModelForm
from django import forms
from .models import Booking, Package_Booking
from datetime import datetime

# Create the form class.

class BookingForm(ModelForm):
    guest_name = forms.CharField(required=True, label='Name')
    start_date = forms.DateField(required=True, label='Check in Date', widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.now().date()}))
    end_date = forms.DateField(required=True, label='Check out Date', widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.now().date()}))
    class Meta:
        model = Booking
        exclude = ['active', 'room']


class PackageBookingForm(ModelForm):

    class Meta:
        model = Package_Booking
        exclude = ['package','active']
