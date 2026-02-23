from rest_framework import serializers
from referrals.models import ReferralBonus, NewAgentBonus


class ReferralBonusSerializer(serializers.ModelSerializer):
    triggered_by_agent_name = serializers.CharField(source='triggered_by_agent.name', read_only=True)

    class Meta:
        model = ReferralBonus
        fields = ['id', 'deal_number', 'amount', 'triggered_by_agent_name', 'created_at']


class NewAgentBonusSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.client_name', read_only=True)

    class Meta:
        model = NewAgentBonus
        fields = ['id', 'deal_number', 'amount', 'client_name', 'created_at']
