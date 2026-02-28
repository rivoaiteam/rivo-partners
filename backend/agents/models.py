import uuid
import random
import string
from django.db import models


def generate_agent_code():
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=4))
    return f'RIVO-{suffix}'


class Agent(models.Model):
    AGENT_TYPE_CHOICES = [
        ('RE_BROKER', 'RE Broker'),
        ('MORTGAGE_BROKER', 'Mortgage Broker'),
        ('OTHER', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, default='')
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, default='')
    agent_type = models.CharField(max_length=20, choices=AGENT_TYPE_CHOICES, blank=True, default='')
    agent_type_other = models.CharField(max_length=255, blank=True, default='')
    rera_number = models.CharField(max_length=50, blank=True, default='')
    agent_code = models.CharField(max_length=20, unique=True, default=generate_agent_code)
    referred_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referred_agents'
    )
    device_token = models.CharField(max_length=255, blank=True, default='')
    is_whatsapp_business = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)
    has_completed_first_action = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agents'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name or self.phone} ({self.agent_code})'

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def save(self, *args, **kwargs):
        self.is_profile_complete = bool(self.name and self.agent_type and self.email)
        super().save(*args, **kwargs)

    @property
    def total_earned(self):
        from django.db.models import Sum
        client_total = self.clients.filter(status='DISBURSED').aggregate(
            total=Sum('commission_amount')
        )['total'] or 0
        bonus_total = self.referral_bonuses.aggregate(
            total=Sum('amount')
        )['total'] or 0
        return client_total + bonus_total

    @property
    def pending_amount(self):
        from django.db.models import Sum
        return self.clients.filter(
            status__in=['PREAPPROVED', 'FOL_RECEIVED']
        ).aggregate(total=Sum('estimated_commission'))['total'] or 0

    @property
    def disbursed_count(self):
        return self.clients.filter(status='DISBURSED').count()

    @property
    def this_month_earned(self):
        from django.utils import timezone
        from django.db.models import Sum
        now = timezone.now()
        return self.clients.filter(
            status='DISBURSED',
            updated_at__year=now.year,
            updated_at__month=now.month,
        ).aggregate(total=Sum('commission_amount'))['total'] or 0


class WhatsAppSession(models.Model):
    """Temporary session for WhatsApp-based auth.
    Backend generates a short code, user sends it via WhatsApp.
    YCloud webhook matches the code + phone → auto-creates/finds agent."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=10, unique=True)
    referral_code = models.CharField(max_length=20, blank=True, default='')
    is_whatsapp_business = models.BooleanField(default=False)
    # Filled when YCloud webhook fires
    phone = models.CharField(max_length=20, blank=True, default='')
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL)
    device_token = models.CharField(max_length=255, blank=True, default='')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'whatsapp_sessions'
        indexes = [
            models.Index(fields=['is_verified', '-created_at']),
        ]

    def __str__(self):
        return f'Code {self.code} - verified={self.is_verified}'
