
from django.urls import path
from . import views

app_name = 'jokes'

urlpatterns = [
    path('', views.home, name='home'),
    path('jokes/', views.joke_list, name='list'),
    path('joke/<int:joke_id>/', views.joke_detail, name='detail'),
    path('random/', views.random_joke, name='random'),
    path('rate/<int:joke_id>/', views.rate_joke, name='rate'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
]
