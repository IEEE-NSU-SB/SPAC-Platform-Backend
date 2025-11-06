
from django.urls import path
from .views import *

app_name='main_web'

urlpatterns = [
    path('', homepage, name='homepage'),
    path('event-details', event_details, name='event_details'),
    path('organizers', organizers, name='organizers'),
    path('timeline', timeline, name='timeline'),
]
    
