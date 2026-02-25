import uuid
from django.db import models


class ReferralBonus(models.Model):
    """Bonus earned by a referrer when their referred agents' deals get disbursed."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey(
        'agents.Agent', on_delete=models.CASCADE, related_name='referral_bonuses'
    )
    triggered_by_agent = models.ForeignKey(
        'agents.Agent', on_delete=models.CASCADE, related_name='triggered_referrer_bonuses'
    )
    triggered_by_client = models.ForeignKey(
        'clients.Client', on_delete=models.CASCADE, related_name='referral_bonuses'
    )
    deal_number = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'referral_bonuses'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['referrer', 'deal_number'],
                name='unique_referrer_deal_number'
            ),
        ]

    def __str__(self):
        return f'Referrer {self.referrer} - Deal #{self.deal_number} - AED {self.amount}'


class NewAgentBonus(models.Model):
    """Bonus earned by a new agent on their first N deals (configurable via AppConfig)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        'agents.Agent', on_delete=models.CASCADE, related_name='new_agent_bonuses'
    )
    client = models.ForeignKey(
        'clients.Client', on_delete=models.CASCADE, related_name='new_agent_bonuses'
    )
    deal_number = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'new_agent_bonuses'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['agent', 'deal_number'],
                name='unique_agent_deal_number'
            ),
        ]

    def __str__(self):
        return f'Agent {self.agent} - Deal #{self.deal_number} - AED {self.amount}'
