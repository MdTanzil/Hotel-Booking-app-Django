from django.urls import path
from  . views import home

app_name = 'hotelbooking'
urlpatterns = [
    path('', home, name='home'),
]
