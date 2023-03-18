from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from . models import Room,Package,Booking
from django.db.models import Q

# Create your views here.

class HomeTemplate(TemplateView):
    template_name = "hotelbooking/index.html"


def search(request):
    print('called')
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        print(start_date)
        end_date = request.POST.get('end_date')
        available_rooms = Room.objects.filter(Q(reservations__start_date__lte=end_date, reservations__end_date__gte=start_date))
        context = {'available_rooms': available_rooms}
        return render(request, 'available_rooms.html', context)
    else:
        return render(request, 'hotelbooking/index.html')

class RoomsTemplate(ListView):
    template_name = "hotelbooking/rooms.html"
    context_object_name = 'rooms'
    queryset = Room.objects.all().filter(active=True)



class PackageTemplate(ListView):
    template_name = "hotelbooking/package.html"
    context_object_name = 'packages'
    queryset = Package.objects.all().filter(active=True)
    
