
from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ваш email', 'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Тема сообщения', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'placeholder': 'Ваше сообщение', 'rows': 5, 'class': 'form-control'}),
        }
