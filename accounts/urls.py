from django.urls import path
from . import views

urlpatterns = [
    path('authentification/', views.authent, name='authent'),
]