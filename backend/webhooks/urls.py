from django.urls import path
from webhooks import views

urlpatterns = [
    path('client-status/', views.client_status_webhook, name='webhook-client-status'),
    path('ycloud/', views.ycloud_webhook, name='webhook-ycloud'),
]
