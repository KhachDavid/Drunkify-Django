from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='music-player-login'),
    path('recover/', views.recover, name='music-player-recover'),
]