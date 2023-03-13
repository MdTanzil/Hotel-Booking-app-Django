from django.contrib import admin
from . models import Room_category, Room_view, Room,Package_item,Package

# Register your models here.
admin.site.register(Room_category)
admin.site.register(Room_view)
admin.site.register(Room)
admin.site.register(Package_item)
admin.site.register(Package)
