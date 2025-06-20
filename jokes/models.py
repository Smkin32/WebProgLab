
from django.db import models
from django.utils import timezone

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.name}: {self.subject}"

class Joke(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'Общие'),
        ('political', 'Политические'),
        ('family', 'Семейные'),
        ('work', 'Рабочие'),
        ('student', 'Студенческие'),
        ('medical', 'Медицинские'),
        ('programming', 'Про программистов'),
    ]
    
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    views = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title or f"Анекдот #{self.id}"
    
    def get_short_content(self):
        return self.content[:100] + "..." if len(self.content) > 100 else self.content
