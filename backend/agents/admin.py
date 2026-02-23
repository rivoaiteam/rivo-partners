from django.contrib import admin
from agents.models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'agent_code', 'agent_type', 'is_profile_complete', 'is_active', 'created_at']
    list_filter = ['agent_type', 'is_profile_complete', 'is_active', 'created_at']
    search_fields = ['name', 'phone', 'agent_code', 'email']
    readonly_fields = ['id', 'agent_code', 'device_token', 'created_at', 'updated_at']
    raw_id_fields = ['referred_by']
