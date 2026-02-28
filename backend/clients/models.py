import uuid
from django.db import models
from decimal import Decimal


class Client(models.Model):
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('CONTACTED', 'Contacted'),
        ('QUALIFIED', 'Qualified'),
        ('SUBMITTED_TO_BANK', 'Submitted to Bank'),
        ('PREAPPROVED', 'Preapproved'),
        ('FOL_RECEIVED', 'FOL Received'),
        ('DISBURSED', 'Disbursed'),
        ('DECLINED', 'Declined'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_name = models.CharField(max_length=255)
    client_phone = models.CharField(max_length=20)
    expected_mortgage_amount = models.DecimalField(max_digits=15, decimal_places=2)
    estimated_commission = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    source_agent = models.ForeignKey(
        'agents.Agent', null=True, blank=True, on_delete=models.SET_NULL, related_name='clients'
    )
    channel = models.CharField(max_length=50, default='PARTNER_PWA')
    crm_lead_id = models.UUIDField(blank=True, null=True, db_index=True, help_text='Lead ID from Rivo CRM')
    consent_given = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['source_agent', 'status']),
        ]

    def __str__(self):
        return f'{self.client_name} - {self.status}'

    def save(self, *args, **kwargs):
        if not self.estimated_commission and self.expected_mortgage_amount:
            from config.models import AppConfig
            min_rate = AppConfig.get_value('commission_min_percent', 0.45)
            self.estimated_commission = self.expected_mortgage_amount * Decimal(str(min_rate)) / 100
        super().save(*args, **kwargs)
