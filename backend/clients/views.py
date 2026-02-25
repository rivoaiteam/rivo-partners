import logging
import requests as http_requests

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from clients.models import Client
from clients.serializers import ClientSerializer, ClientSubmitSerializer
from agents.services import send_client_whatsapp_notification

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_client(request):
    """Submit a new client referral.
    POST /api/v1/clients/ingest"""
    agent = request.user
    serializer = ClientSubmitSerializer(data=request.data, context={'agent': agent})
    serializer.is_valid(raise_exception=True)

    client = Client.objects.create(
        client_name=serializer.validated_data['client_name'],
        client_phone=serializer.validated_data['client_phone'],
        expected_mortgage_amount=serializer.validated_data['expected_mortgage_amount'],
        source_agent=agent,
        channel='PARTNER_PWA',
    )

    # Push lead to Rivo CRM
    crm_payload = {
        'name': client.client_name,
        'phone': client.client_phone,
        'mortgage_amount': float(client.expected_mortgage_amount) if client.expected_mortgage_amount else None,
        'source': agent.name or 'Rivo Partner',
        'channel': 'Freelance Network',
        'referrer_phone': agent.phone,
    }
    try:
        logger.info(f'Pushing lead to CRM: {crm_payload}')
        crm_response = http_requests.post(
            'https://rivo-backend-331738587654.asia-southeast1.run.app/api/leads/ingest/',
            json=crm_payload,
            timeout=10,
        )
        logger.info(f'CRM response [{crm_response.status_code}]: {crm_response.text[:500]}')
        if crm_response.status_code in (200, 201):
            try:
                crm_data = crm_response.json()
                if crm_data.get('lead_id'):
                    client.crm_lead_id = crm_data['lead_id']
                    client.save(update_fields=['crm_lead_id'])
                    logger.info(f'CRM lead_id stored: {crm_data["lead_id"]}')
            except ValueError:
                logger.warning(f'CRM returned 200 but non-JSON body: {crm_response.text[:200]}')
        else:
            logger.warning(f'CRM rejected lead: {crm_response.status_code} — {crm_response.text[:500]}')
    except Exception as e:
        logger.error(f'Failed to push lead to Rivo CRM: {e}')

    # Mark agent's first action
    if not agent.has_completed_first_action:
        agent.has_completed_first_action = True
        agent.save(update_fields=['has_completed_first_action'])

    # Send WhatsApp notification to client
    send_client_whatsapp_notification(
        client.client_phone,
        agent.name or 'A Rivo Partner agent',
        client.client_name,
    )

    return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_clients(request):
    """Get all clients referred by the authenticated agent.
    Supports search by name and filter by status."""
    agent = request.user
    clients = Client.objects.filter(source_agent=agent)

    # Search by client name
    search = request.query_params.get('search', '').strip()
    if search:
        clients = clients.filter(client_name__icontains=search)

    # Filter by status
    status_filter = request.query_params.get('status', '').strip().upper()
    if status_filter and status_filter != 'ALL':
        clients = clients.filter(status=status_filter)

    serializer = ClientSerializer(clients, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_detail(request, client_id):
    """Get details of a specific client."""
    agent = request.user
    try:
        client = Client.objects.get(id=client_id, source_agent=agent)
    except Client.DoesNotExist:
        return Response({'error': 'Client not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(ClientSerializer(client).data)
