from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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

    return Response({
        'referral_bonuses': {
            'items': ReferralBonusSerializer(referral_bonuses, many=True).data,
            'total': sum(b.amount for b in referral_bonuses),
            'count': referral_bonuses.count(),
            'max': 3,
            'completed': referral_bonuses.count() >= 3,
        },
        'deal_bonuses': {
            'items': NewAgentBonusSerializer(deal_bonuses, many=True).data,
            'total': sum(b.amount for b in deal_bonuses),
            'count': deal_bonuses.count(),
            'max': 3,
            'completed': deal_bonuses.count() >= 3,
        },
    })
