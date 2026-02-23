from django.urls import path
from clients import views

urlpatterns = [
    path('ingest/', views.submit_client, name='client-submit'),
    path('', views.list_clients, name='client-list'),
    path('<uuid:client_id>/', views.client_detail, name='client-detail'),
]
