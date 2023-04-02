from django.shortcuts import render
from django.shortcuts import redirect
from datetime import datetime, date, timedelta
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView
from . models import Room, Package, Booking, Room_category,Package_Booking
from django.db.models import Q
from .form import BookingForm ,PackageBookingForm
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


class HomeTemplate(TemplateView):
    
    template_name = "hotelbooking/index.html"



class RoomsTemplate(View):
    def get(self,request):
        today = date.today()

        # Calculate tomorrow's date
        tomorrow = today + timedelta(days=1)

       # Get a list of all booked rooms for today and tomorrow
        booked_rooms = Booking.objects.filter(start_date__lte=today, end_date__gt=today) | Booking.objects.filter(start_date__lt=tomorrow, end_date__gte=tomorrow)

        # Get a list of all rooms that are not booked today or tomorrow
        id_list = []
        for i in booked_rooms:
            id_list.append(i.room.id)
        available_rooms = Room.objects.exclude(id__in=id_list).filter(active=True)
        all_rooms = Room.objects.all().filter(active=True)
        template_name = "hotelbooking/rooms.html"
        context = {
            "rooms": available_rooms,
            'all_rooms': all_rooms
        }
        return render(request, template_name,context)
        
    def post(self,request):
        template_name = "hotelbooking/rooms.html"
        context ={}
        try: 
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            room_type = request.POST.get('room_type')
            booking_data = Booking.objects.filter(~Q(start_date__lte=end_date, end_date__gte=start_date))
            
            id_list =[]
            for i in booking_data:
                id_list.append(i.room.id)
            rooms = Room.objects.filter(id__in=id_list)
            template_name = "hotelbooking/searchroom.html"
            context = {
                "rooms": rooms,
                "start_date": start_date,
                "end_date": end_date
            }
            return render(request, template_name, context)
        except:
            return render(request, template_name)
    

class PackageTemplate(ListView):
    template_name = "hotelbooking/package.html"
    context_object_name = 'packages'
    queryset = Package.objects.all().filter(active=True)
    

class RoomDetails(LoginRequiredMixin, TemplateView):
   
    def get(self,request,pk):
        try:
            if request.GET:
                if request.GET.get("choice") == "booking":
                    return redirect(f"/booking-room/{pk}")
                elif request.GET.get("choice") == "confirm_booking":
                    return redirect(f"/booking-room/{pk}")
                else:
                    pass
                
            
        except:
            pass

            
        
        room = Room.objects.get(id = pk)
        template_name = "hotelbooking/rooms-single.html"
        context = {
            "room" : room,
        }
        return render(request, template_name, context)


class CreateBookingRoom(LoginRequiredMixin,View ):
    def get(self, request, pk):
        id=pk
        form = BookingForm()
        template_name = "hotelbooking/createBooking.html"
        context = {
            'form': form,
            'id':pk
        }
        return render(request, template_name, context)

    def post(self, request, pk):
        room = Room.objects.get(id =pk)
        form = BookingForm(request.POST, instance=Booking(room=room))
        if form.is_valid() :
            form.save()
        return render(request, 'hotelbooking/rooms.html')


class PackageBookingCreateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        id = pk
        form = PackageBookingForm()
        template_name = "hotelbooking/create_package_booking.html"
        context = {
            'form': form,
            'id': pk
        }
        return render(request, template_name, context)

    def post(self, request, pk):
        package = Package.objects.get(id=pk)
        form = PackageBookingForm(request.POST, instance=Package_Booking(package=package))
        if form.is_valid():
            form.save()
        return render(request, 'hotelbooking/index.html')
