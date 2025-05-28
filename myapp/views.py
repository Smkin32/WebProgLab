
from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return HttpResponse("<h1>Welcome to Django!</h1><p>Your Django app is working correctly.</p>")

def about(request):
    context = {
        'title': 'About Us',
        'message': 'This is a Django application running on Replit!'
    }
    return render(request, 'about.html', context)
