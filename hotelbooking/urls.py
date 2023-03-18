from django.urls import path
from . views import HomeTemplate, RoomsTemplate, PackageTemplate, search

app_name = 'hotelbooking'
urlpatterns = [
    path('', HomeTemplate.as_view(), name='home'),
    path('rooms/', RoomsTemplate.as_view(), name='rooms'),
    path('package/', PackageTemplate.as_view(), name='packages'),
    path('search/', search, name='search'),
]
