import re
from decimal import Decimal
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
def crm_status_webhook(request):
    """Receive lead status updates from Rivo CRM.
    POST /api/v1/webhook/crm-status
    Payload: { "lead_id": "uuid", "pipeline_status": "qualified", "mortgage_amount": "500000.00" }"""

    log = WebhookLog.objects.create(
        source='RIVO_CRM',
        event_type='CRM_STATUS_UPDATE',
        payload=request.data,
    )

    lead_id = request.data.get('lead_id')
    pipeline_status = request.data.get('pipeline_status', '').upper()
    mortgage_amount = request.data.get('mortgage_amount')

    valid_statuses = ['SUBMITTED', 'CONTACTED', 'QUALIFIED', 'SUBMITTED_TO_BANK', 'PREAPPROVED', 'FOL_RECEIVED', 'DISBURSED', 'DECLINED']
    if pipeline_status not in valid_statuses:
        log.error_message = f'Invalid status: {pipeline_status}'
        log.save(update_fields=['error_message'])
        return Response(
            {'error': f'Invalid status. Must be one of: {valid_statuses}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        client = Client.objects.get(crm_lead_id=lead_id)
    except Client.DoesNotExist:
        log.error_message = f'No client with crm_lead_id: {lead_id}'
        log.save(update_fields=['error_message'])
        return Response({'error': 'Lead not found.'}, status=status.HTTP_404_NOT_FOUND)

    old_status = client.status
    client.status = pipeline_status

    if mortgage_amount:
        client.expected_mortgage_amount = Decimal(str(mortgage_amount))
        client.estimated_commission = None  # recalculate on save

    if pipeline_status == 'DISBURSED' and mortgage_amount:
        client.commission_amount = Decimal(str(mortgage_amount))

    client.save()

    if pipeline_status == 'DISBURSED' and old_status != 'DISBURSED':
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

            # Reactivate if previously deleted — reset profile data
            if not created and not agent.is_active:
                agent.is_active = True
                agent.name = ''
                agent.email = ''
                agent.agent_type = ''
                agent.agent_type_other = ''
                agent.rera_number = ''
                agent.is_profile_complete = False
                agent.has_completed_first_action = False
                agent.save()

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
