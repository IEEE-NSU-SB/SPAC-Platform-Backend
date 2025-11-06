from django.shortcuts import render

# Create your views here.

def homepage(request):
    return render(request, 'homepage.html')

def event_details(request):
    return render(request, 'event-details.html')

def organizers(request):
    return render(request, 'organizers.html')

def timeline(request):
    return render(request, 'timeline.html')