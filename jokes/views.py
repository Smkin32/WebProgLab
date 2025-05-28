
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Joke, ContactMessage
from .forms import ContactForm
import random
import requests
import os

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
    try:
        joke = Joke.objects.order_by('?').first()
        if joke:
            return JsonResponse({
                'id': joke.id,
                'content': joke.content,
                'category': joke.get_category_display(),
                'title': joke.title or f'Анекдот #{joke.id}',
            })
        return JsonResponse({'error': 'Анекдоты не найдены'})
    except Exception as e:
        return JsonResponse({'error': 'Ошибка при загрузке анекдота'})

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

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('jokes:home')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    
    form = AuthenticationForm()
    return render(request, 'jokes/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('jokes:home')

def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}! Теперь вы можете войти.')
            login(request, user)
            return redirect('jokes:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    form = UserCreationForm()
    return render(request, 'jokes/register.html', {'form': form})

def send_telegram_message(message_text):
    """Send message to Telegram bot"""
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message_text,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            
            # Format message for Telegram
            telegram_message = f"""
<b>🔔 Новое сообщение с сайта анекдотов</b>

<b>Имя:</b> {contact_message.name}
<b>Email:</b> {contact_message.email}
<b>Тема:</b> {contact_message.subject}

<b>Сообщение:</b>
{contact_message.message}

<b>Дата:</b> {contact_message.created_at.strftime('%d.%m.%Y %H:%M')}
            """
            
            # Send to Telegram
            if send_telegram_message(telegram_message):
                contact_message.is_sent = True
                contact_message.save()
                messages.success(request, 'Ваше сообщение успешно отправлено!')
            else:
                messages.warning(request, 'Сообщение сохранено, но не удалось отправить уведомление.')
            
            return redirect('jokes:contact')
    else:
        form = ContactForm()
    
    return render(request, 'jokes/contact.html', {'form': form})
