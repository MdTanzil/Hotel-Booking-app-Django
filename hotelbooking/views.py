from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from . models import Room,Package

# Create your views here.

class HomeTemplate(TemplateView):
    template_name = "hotelbooking/index.html"


class RoomsTemplate(ListView):
    template_name = "hotelbooking/rooms.html"
    context_object_name = 'rooms'
    queryset = Room.objects.all().filter(active=True)


class PackageTemplate(ListView):
    template_name = "hotelbooking/package.html"
    context_object_name = 'packages'
    queryset = Package.objects.all().filter(active=True)
    
