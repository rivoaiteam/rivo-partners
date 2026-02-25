from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.models import AppConfig
from referrals.models import ReferralBonus, NewAgentBonus
from referrals.serializers import ReferralBonusSerializer, NewAgentBonusSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bonuses(request):
    """Get all bonuses earned by the authenticated agent.
    Includes both referral bonuses (as referrer) and new agent deal bonuses."""
    agent = request.user

    referral_bonuses = ReferralBonus.objects.filter(referrer=agent)
    deal_bonuses = NewAgentBonus.objects.filter(agent=agent)

    referrer_config = AppConfig.get_value('referrer_bonuses', [500, 500, 1000])
    deal_config = AppConfig.get_value('new_agent_bonuses', [1000, 750, 500])
    referrer_max = len(referrer_config)
    deal_max = len(deal_config)

    return Response({
        'referral_bonuses': {
            'items': ReferralBonusSerializer(referral_bonuses, many=True).data,
            'total': sum(b.amount for b in referral_bonuses),
            'count': referral_bonuses.count(),
            'max': referrer_max,
            'completed': referral_bonuses.count() >= referrer_max,
        },
        'deal_bonuses': {
            'items': NewAgentBonusSerializer(deal_bonuses, many=True).data,
            'total': sum(b.amount for b in deal_bonuses),
            'count': deal_bonuses.count(),
            'max': deal_max,
            'completed': deal_bonuses.count() >= deal_max,
        },
    })
