
from django.contrib import admin
from .models import Joke

@admin.register(Joke)
class JokeAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'rating', 'views', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['views', 'created_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'category')
        }),
        ('Статистика', {
            'fields': ('rating', 'views', 'created_at'),
            'classes': ('collapse',)
        }),
    )
