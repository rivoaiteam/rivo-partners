from django.urls import path
from webhooks import views

urlpatterns = [
    path('crm-status/', views.crm_status_webhook, name='webhook-crm-status'),
    path('ycloud/', views.ycloud_webhook, name='webhook-ycloud'),
]
