import os
import random
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from agents.models import Agent, WhatsAppSession
from agents.serializers import (
    AgentSerializer,
    AgentProfileUpdateSerializer,
    NetworkAgentSerializer,
)
from agents.services import generate_device_token
from referrals.models import ReferralBonus
from referrals.serializers import ReferralBonusSerializer


def _generate_code():
    """Generate a unique 6-digit verification code."""
    while True:
        code = str(random.randint(100000, 999999))
        if not WhatsAppSession.objects.filter(code=code, is_verified=False).exists():
            return code


@api_view(['POST'])
@permission_classes([AllowAny])
def init_whatsapp(request):
    """Step 1: Frontend calls this before opening WhatsApp.
    Returns a verification code and WhatsApp deep link URL.
    The pre-filled message contains the code. User just taps send."""
    referral_code = request.data.get('referral_code', '')
    is_business = request.data.get('is_whatsapp_business', False)

    code = _generate_code()

    WhatsAppSession.objects.create(
        code=code,
        referral_code=referral_code,
        is_whatsapp_business=is_business,
    )

    whatsapp_number = os.getenv('YCLOUD_WHATSAPP_NUMBER', '').lstrip('+')
    message = f'RIVO {code}'

    whatsapp_url = f'https://wa.me/{whatsapp_number}?text={message}'

    return Response({
        'code': code,
        'whatsapp_url': whatsapp_url,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_verification(request, code):
    """Step 2: Frontend polls this after user sends WhatsApp message.
    Returns verified=false until YCloud webhook processes the message.
    Once verified, returns agent data and auth token."""
    try:
        session = WhatsAppSession.objects.get(code=code)
    except WhatsAppSession.DoesNotExist:
        return Response({'error': 'Invalid code.'}, status=status.HTTP_404_NOT_FOUND)

    if not session.is_verified:
        return Response({'verified': False})

    return Response({
        'verified': True,
        'agent': AgentSerializer(session.agent).data,
        'token': session.device_token,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Get current authenticated agent's profile and earnings."""
    agent = request.user
    return Response(AgentSerializer(agent).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update agent profile fields."""
    agent = request.user
    serializer = AgentProfileUpdateSerializer(agent, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(AgentSerializer(agent).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def network(request):
    """Get agent's referral network — referred agents and bonus status."""
    agent = request.user
    referred_agents = agent.referred_agents.all()

    bonuses = ReferralBonus.objects.filter(referrer=agent)
    total_bonuses_earned = sum(b.amount for b in bonuses)
    bonuses_completed = bonuses.count() >= 3

    return Response({
        'agent_code': agent.agent_code,
        'referred_agents': NetworkAgentSerializer(
            referred_agents, many=True, context={'referrer': agent}
        ).data,
        'bonus_summary': {
            'total_earned': total_bonuses_earned,
            'bonuses_count': bonuses.count(),
            'max_bonuses': 3,
            'completed': bonuses_completed,
            'bonuses': ReferralBonusSerializer(bonuses, many=True).data,
        },
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def resolve_referral_code(request, code):
    """Resolve a referral code to an agent name. Used on landing page."""
    try:
        agent = Agent.objects.get(agent_code=code)
        return Response({'agent_name': agent.name or 'A Rivo Partner'})
    except Agent.DoesNotExist:
        return Response({'error': 'Invalid referral code.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout — clear device token and delete associated WhatsApp sessions."""
    agent = request.user
    # Delete all WhatsApp sessions for this agent
    WhatsAppSession.objects.filter(agent=agent).delete()
    # Clear device token
    agent.device_token = ''
    agent.save(update_fields=['device_token'])
    return Response({'message': 'Logged out successfully.'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Soft-delete agent account."""
    agent = request.user
    agent.is_active = False
    agent.device_token = ''
    agent.save(update_fields=['is_active', 'device_token'])
    return Response({'message': 'Account deleted.'})
