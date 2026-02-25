import logging
import os
import random
import requests as http_requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from agents.models import Agent, WhatsAppSession
from agents.serializers import (
    AgentSerializer,
    AgentProfileUpdateSerializer,
    NetworkAgentSerializer,
)
from agents.services import generate_device_token
from config.models import AppConfig
from referrals.models import ReferralBonus
from referrals.serializers import ReferralBonusSerializer

logger = logging.getLogger(__name__)


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

    message = f'RIVO {code}'

    if is_business:
        base_url = AppConfig.get_value('whatsapp_business', 'https://wa.me/971545079577')
    else:
        base_url = AppConfig.get_value('whatsapp_personal', 'https://wa.me/971545079577')

    whatsapp_url = f'{base_url}?text={message}'

    logger.info(f'WhatsApp session created: code={code}, referral={referral_code or "none"}')

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
    logger.info(f'Profile updated: agent={agent.phone}, fields={list(request.data.keys())}')
    return Response(AgentSerializer(agent).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def network(request):
    """Get agent's referral network — referred agents and bonus status."""
    agent = request.user
    referred_agents = agent.referred_agents.all()

    bonuses = ReferralBonus.objects.filter(referrer=agent)
    total_bonuses_earned = sum(b.amount for b in bonuses)
    bonus_config = AppConfig.get_value('referrer_bonuses', [500, 500, 1000])
    max_bonuses = len(bonus_config)
    bonuses_completed = bonuses.count() >= max_bonuses

    return Response({
        'agent_code': agent.agent_code,
        'referred_agents': NetworkAgentSerializer(
            referred_agents, many=True, context={'referrer': agent}
        ).data,
        'bonus_summary': {
            'total_earned': total_bonuses_earned,
            'bonuses_count': bonuses.count(),
            'max_bonuses': max_bonuses,
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
    WhatsAppSession.objects.filter(agent=agent).delete()
    agent.device_token = ''
    agent.save(update_fields=['device_token'])
    logger.info(f'Agent logged out: {agent.phone}')
    return Response({'message': 'Logged out successfully.'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Soft-delete agent account."""
    agent = request.user
    agent.is_active = False
    agent.device_token = ''
    agent.save(update_fields=['is_active', 'device_token'])
    logger.info(f'Account deleted: {agent.phone}')
    return Response({'message': 'Account deleted.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_google(request):
    """Verify Google ID token and save email to agent profile."""
    credential = request.data.get('credential', '')
    if not credential:
        return Response({'error': 'Missing credential.'}, status=status.HTTP_400_BAD_REQUEST)

    google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    if not google_client_id:
        logger.error('GOOGLE_CLIENT_ID env var not set')
        return Response({'error': 'Google OAuth not configured.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        idinfo = id_token.verify_oauth2_token(credential, google_requests.Request(), google_client_id)
        email = idinfo.get('email', '')
        if not email:
            return Response({'error': 'No email in Google token.'}, status=status.HTTP_400_BAD_REQUEST)

        agent = request.user
        agent.email = email
        agent.save(update_fields=['email'])
        logger.info(f'Google connected: agent={agent.phone}, email={email}')
        return Response(AgentSerializer(agent).data)
    except ValueError as e:
        logger.warning(f'Invalid Google token for agent {request.user.phone}: {e}')
        return Response({'error': 'Invalid Google token.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_outlook(request):
    """Exchange Microsoft auth code for email and save to agent profile."""
    code = request.data.get('code', '')
    redirect_uri = request.data.get('redirect_uri', '')
    if not code:
        return Response({'error': 'Missing auth code.'}, status=status.HTTP_400_BAD_REQUEST)

    client_id = os.getenv('MICROSOFT_CLIENT_ID', '')
    client_secret = os.getenv('MICROSOFT_CLIENT_SECRET', '')
    if not client_id or not client_secret:
        logger.error('MICROSOFT_CLIENT_ID or MICROSOFT_CLIENT_SECRET env var not set')
        return Response({'error': 'Microsoft OAuth not configured.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        # Exchange auth code for token
        token_response = http_requests.post(
            'https://login.microsoftonline.com/common/oauth2/v2.0/token',
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
                'scope': 'openid email profile',
            },
        )
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        if not access_token:
            logger.warning(f'Microsoft token exchange failed: {token_data}')
            return Response({'error': 'Failed to get Microsoft token.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get user profile
        profile_response = http_requests.get(
            'https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': f'Bearer {access_token}'},
        )
        profile = profile_response.json()
        email = profile.get('mail') or profile.get('userPrincipalName', '')
        if not email:
            logger.warning(f'No email in Microsoft profile: {profile}')
            return Response({'error': 'No email from Microsoft.'}, status=status.HTTP_400_BAD_REQUEST)

        agent = request.user
        agent.email = email
        agent.save(update_fields=['email'])
        logger.info(f'Outlook connected: agent={agent.phone}, email={email}')
        return Response(AgentSerializer(agent).data)
    except Exception as e:
        logger.error(f'Microsoft auth failed for agent {request.user.phone}: {e}')
        return Response({'error': 'Microsoft auth failed.'}, status=status.HTTP_400_BAD_REQUEST)
