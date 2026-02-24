from django.urls import path
from agents import views

urlpatterns = [
    path('init-whatsapp/', views.init_whatsapp, name='init-whatsapp'),
    path('check-verification/<str:code>/', views.check_verification, name='check-verification'),
    path('me/', views.me, name='agent-me'),
    path('profile/', views.update_profile, name='agent-update-profile'),
    path('network/', views.network, name='agent-network'),
    path('referral/<str:code>/', views.resolve_referral_code, name='agent-resolve-referral'),
    path('logout/', views.logout, name='agent-logout'),
    path('delete/', views.delete_account, name='agent-delete'),
    path('connect-google/', views.connect_google, name='agent-connect-google'),
    path('connect-outlook/', views.connect_outlook, name='agent-connect-outlook'),
]
