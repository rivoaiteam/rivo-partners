from django.urls import path
from referrals import views

urlpatterns = [
    path('bonuses/', views.my_bonuses, name='my-bonuses'),
]
