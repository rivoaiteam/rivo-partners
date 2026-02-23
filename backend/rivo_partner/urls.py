from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/agents/', include('agents.urls')),
    path('api/v1/clients/', include('clients.urls')),
    path('api/v1/config/', include('config.urls')),
    path('api/v1/referrals/', include('referrals.urls')),
    path('api/v1/webhook/', include('webhooks.urls')),
]
