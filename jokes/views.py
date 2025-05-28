
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Joke
import random

def home(request):
    # Get latest jokes
    latest_jokes = Joke.objects.all()[:10]
    # Get random joke of the day
    joke_of_day = Joke.objects.order_by('?').first() if Joke.objects.exists() else None
    
    context = {
        'latest_jokes': latest_jokes,
        'joke_of_day': joke_of_day,
        'categories': Joke.CATEGORY_CHOICES,
    }
    return render(request, 'jokes/home.html', context)

def joke_list(request):
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    jokes = Joke.objects.all()
    
    if category:
        jokes = jokes.filter(category=category)
    
    if search:
        jokes = jokes.filter(
            Q(content__icontains=search) | Q(title__icontains=search)
        )
    
    paginator = Paginator(jokes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category': category,
        'search': search,
        'categories': Joke.CATEGORY_CHOICES,
    }
    return render(request, 'jokes/list.html', context)

def joke_detail(request, joke_id):
    joke = get_object_or_404(Joke, id=joke_id)
    # Increment views
    joke.views += 1
    joke.save()
    
    # Get related jokes from same category
    related_jokes = Joke.objects.filter(category=joke.category).exclude(id=joke.id)[:5]
    
    context = {
        'joke': joke,
        'related_jokes': related_jokes,
    }
    return render(request, 'jokes/detail.html', context)

def random_joke(request):
    joke = Joke.objects.order_by('?').first()
    if joke:
        return JsonResponse({
            'id': joke.id,
            'content': joke.content,
            'category': joke.get_category_display(),
        })
    return JsonResponse({'error': 'No jokes found'})

def rate_joke(request, joke_id):
    if request.method == 'POST':
        joke = get_object_or_404(Joke, id=joke_id)
        action = request.POST.get('action')
        
        if action == 'up':
            joke.rating += 1
        elif action == 'down':
            joke.rating -= 1
        
        joke.save()
        return JsonResponse({'rating': joke.rating})
    
    return JsonResponse({'error': 'Invalid request'})
