from django.contrib import admin
from . models import Room_category, Room_view, Room, Package_item, Package, Booking,Package_Booking

# Register your models here.
class Room_categoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'desc')
    

@admin.register(Room_view)
class Room_viewAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc')
    
    
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'room_price', 'max_person',
                    'room_size', 'room_category')
    

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name','room','price')
    


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display =('guest_name','room','start_date','end_date')
    

@admin.register(Package_Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_number')




admin.site.register(Room_category,Room_categoryAdmin)
admin.site.register(Package_item)
