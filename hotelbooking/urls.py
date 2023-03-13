from django.urls import path
from . views import HomeTemplate, RoomsTemplate, PackageTemplate

app_name = 'hotelbooking'
urlpatterns = [
    path('', HomeTemplate.as_view(), name='home'),
    path('rooms/', RoomsTemplate.as_view(), name='rooms'),
    path('package/', PackageTemplate.as_view(), name='packages'),
]
