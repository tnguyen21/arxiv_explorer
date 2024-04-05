from django.urls import path
from . import views

urlpatterns = [
    path('', views.profiles, name='profiles'),
    path('like/', views.like_profile, name='like_profile'),
]
