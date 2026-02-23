import re
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from agents.models import Agent, WhatsAppSession
from agents.services import generate_device_token
from clients.models import Client
from webhooks.models import WebhookLog
from referrals.services import process_disbursal_bonuses


@api_view(['POST'])
@permission_classes([AllowAny])
def client_status_webhook(request):
    """Receive client status updates from Rivo OS.
    POST /api/v1/webhook/client-status
    Statuses: Submitted -> Contacted -> Qualified -> Approved -> Disbursed"""

    log = WebhookLog.objects.create(
        source='RIVO_OS',
        event_type='CLIENT_STATUS_UPDATE',
        payload=request.data,
    )

    client_id = request.data.get('client_id')
    new_status = request.data.get('status', '').upper()
    commission_amount = request.data.get('commission_amount')

    valid_statuses = ['SUBMITTED', 'CONTACTED', 'QUALIFIED', 'APPROVED', 'DISBURSED']
    if new_status not in valid_statuses:
        log.error_message = f'Invalid status: {new_status}'
        log.save(update_fields=['error_message'])
        return Response(
            {'error': f'Invalid status. Must be one of: {valid_statuses}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        log.error_message = f'Client not found: {client_id}'
        log.save(update_fields=['error_message'])
        return Response({'error': 'Client not found.'}, status=status.HTTP_404_NOT_FOUND)

    old_status = client.status
    client.status = new_status

    if commission_amount and new_status == 'DISBURSED':
        from decimal import Decimal
        client.commission_amount = Decimal(str(commission_amount))

    client.save()

    if new_status == 'DISBURSED' and old_status != 'DISBURSED':
        process_disbursal_bonuses(client)

    log.processed = True
    log.save(update_fields=['processed'])

    return Response({'message': 'Status updated successfully.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def ycloud_webhook(request):
    """Receive incoming WhatsApp messages from YCloud.
    When a user sends 'RIVO-VERIFY-XXXXXXXX', match to a pending session,
    auto-create/find agent by phone, and mark session as verified."""

    log = WebhookLog.objects.create(
        source='YCLOUD',
        event_type=request.data.get('type', 'UNKNOWN'),
        payload=request.data,
    )

    event_type = request.data.get('type', '')

    # Handle incoming WhatsApp message
    if event_type == 'whatsapp.inbound_message.received':
        wa_message = request.data.get('whatsappInboundMessage', {})
        from_phone = wa_message.get('from', '')
        text = wa_message.get('text', {}).get('body', '') if isinstance(wa_message.get('text'), dict) else ''

        # Also handle plain text body
        if not text:
            text = wa_message.get('text', '') if isinstance(wa_message.get('text'), str) else ''

        # Extract verification code from message: RIVO 123456
        match = re.search(r'RIVO\s*(\d{6})', text.upper())
        if match and from_phone:
            code = match.group(1)

            try:
                session = WhatsAppSession.objects.get(
                    code=code,
                    is_verified=False,
                )
            except WhatsAppSession.DoesNotExist:
                log.error_message = f'Code not found or already verified: {code}'
                log.save(update_fields=['error_message'])
                return Response({'message': 'Session not found.'})

            # Normalize phone — ensure it has + prefix
            phone = from_phone if from_phone.startswith('+') else f'+{from_phone}'

            # Find or create agent by phone
            agent, created = Agent.objects.get_or_create(
                phone=phone,
                defaults={
                    'is_whatsapp_business': session.is_whatsapp_business,
                },
            )

            # Reactivate if previously deleted
            if not created and not agent.is_active:
                agent.is_active = True
                agent.save(update_fields=['is_active'])

            # Handle referral code for new agents
            if created and session.referral_code:
                try:
                    referrer = Agent.objects.get(agent_code=session.referral_code)
                    agent.referred_by = referrer
                    agent.save(update_fields=['referred_by'])
                except Agent.DoesNotExist:
                    pass

            # Generate device token and mark session verified
            device_token = generate_device_token()
            agent.device_token = device_token
            agent.save(update_fields=['device_token'])

            session.phone = phone
            session.agent = agent
            session.device_token = device_token
            session.is_verified = True
            session.save()

            log.processed = True
            log.save(update_fields=['processed'])

            return Response({'message': 'Agent verified successfully.'})

    log.processed = True
    log.save(update_fields=['processed'])
    return Response({'message': 'Webhook received.'})
