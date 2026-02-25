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
        disbursed = self.clients.filter(status='DISBURSED')
        total = sum(c.commission_amount or 0 for c in disbursed)
        total += self.referral_bonuses_earned
        return total

    @property
    def pending_amount(self):
        active = self.clients.filter(status='APPROVED')
        return sum(c.estimated_commission or 0 for c in active)

    @property
    def disbursed_count(self):
        return self.clients.filter(status='DISBURSED').count()

    @property
    def this_month_earned(self):
        from django.utils import timezone
        now = timezone.now()
        disbursed = self.clients.filter(
            status='DISBURSED',
            updated_at__year=now.year,
            updated_at__month=now.month,
        )
        return sum(c.commission_amount or 0 for c in disbursed)

    @property
    def referral_bonuses_earned(self):
        from referrals.models import ReferralBonus
        bonuses = ReferralBonus.objects.filter(referrer=self)
        return sum(b.amount for b in bonuses)

    @property
    def network_disbursal_count(self):
        """Total disbursals across all referred agents."""
        from clients.models import Client
        referred_agent_ids = self.referred_agents.values_list('id', flat=True)
        return Client.objects.filter(
            source_agent_id__in=referred_agent_ids,
            status='DISBURSED'
        ).count()


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

    def __str__(self):
        return f'Code {self.code} - verified={self.is_verified}'
