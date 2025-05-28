from django.contrib import admin
from .models import Joke, ContactMessage

@admin.register(Joke)
class JokeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'rating', 'views', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'views')
    ordering = ('-created_at',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_sent', 'created_at')
    list_filter = ('is_sent', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)