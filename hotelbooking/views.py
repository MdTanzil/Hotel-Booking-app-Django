from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class HomeTemplate(TemplateView):
    template_name = "hotelbooking/index.html"
