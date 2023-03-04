from django.urls import path
from  . views import HomeTemplate

app_name = 'hotelbooking'
urlpatterns = [
    path('', HomeTemplate.as_view(), name='home'),
]
