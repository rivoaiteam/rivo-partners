from django.contrib import admin
from clients.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_phone', 'expected_mortgage_amount', 'status', 'source_agent', 'created_at']
    list_filter = ['status', 'channel', 'created_at']
    search_fields = ['client_name', 'client_phone']
    readonly_fields = ['id', 'estimated_commission', 'created_at', 'updated_at']
    raw_id_fields = ['source_agent']
