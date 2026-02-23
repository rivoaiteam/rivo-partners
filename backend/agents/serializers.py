from rest_framework import serializers
from agents.models import Agent


class AgentSerializer(serializers.ModelSerializer):
    total_earned = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    pending_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    disbursed_count = serializers.IntegerField(read_only=True)
    this_month_earned = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'phone', 'email', 'agent_type', 'agent_type_other',
            'rera_number', 'agent_code', 'is_whatsapp_business',
            'is_profile_complete', 'has_completed_first_action',
            'total_earned', 'pending_amount', 'disbursed_count', 'this_month_earned',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'agent_code', 'is_profile_complete', 'created_at', 'updated_at']


class AgentProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['name', 'email', 'agent_type', 'agent_type_other', 'rera_number']


class NetworkAgentSerializer(serializers.ModelSerializer):
    """Serializer for agents in the referrer's network."""
    deals_count = serializers.SerializerMethodField()
    bonus_earned = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = ['id', 'name', 'agent_code', 'created_at', 'deals_count', 'bonus_earned']

    def get_deals_count(self, obj):
        return obj.clients.filter(status='DISBURSED').count()

    def get_bonus_earned(self, obj):
        """Bonus earned by the referrer from this specific agent's deals."""
        from referrals.models import ReferralBonus
        referrer = self.context.get('referrer')
        if not referrer:
            return 0
        bonuses = ReferralBonus.objects.filter(
            referrer=referrer,
            triggered_by_agent=obj
        )
        return sum(b.amount for b in bonuses)
