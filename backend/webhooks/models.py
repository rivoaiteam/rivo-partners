import uuid
from django.db import models


class WebhookLog(models.Model):
    """Logs incoming webhooks from Rivo OS and YCloud."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.CharField(max_length=50)  # RIVO_OS, YCLOUD
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webhook_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.source} - {self.event_type} - {self.created_at}'
