from django.urls import path
from config import views

urlpatterns = [
    path('', views.get_config, name='app-config'),
]
