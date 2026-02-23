from django.contrib import admin
from webhooks.models import WebhookLog


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ['source', 'event_type', 'processed', 'created_at']
    list_filter = ['source', 'event_type', 'processed', 'created_at']
    readonly_fields = ['id', 'source', 'event_type', 'payload', 'processed', 'error_message', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
