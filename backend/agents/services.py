import logging
import requests
import uuid
from django.conf import settings

logger = logging.getLogger(__name__)


def send_whatsapp_verification(phone, agent_code):
    """Send WhatsApp verification message via YCloud."""
    url = 'https://api.ycloud.com/v2/whatsapp/messages'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': settings.YCLOUD_API_KEY,
    }
    payload = {
        'from': settings.YCLOUD_WHATSAPP_NUMBER,
        'to': phone,
        'type': 'text',
        'text': {
            'body': f'Your Rivo Partner verification code is: {agent_code}. Welcome to the Rivo Mortgage Referral Network!'
        },
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f'WhatsApp verification failed for {phone}: [{response.status_code}] {response.text}')
        else:
            logger.info(f'WhatsApp verification sent to {phone}')
        return response.status_code == 200, response.json()
    except requests.RequestException as e:
        logger.error(f'WhatsApp verification request failed for {phone}: {e}')
        return False, str(e)


def send_client_whatsapp_notification(client_phone, agent_name, client_name):
    """Send WhatsApp notification to referred client."""
    url = 'https://api.ycloud.com/v2/whatsapp/messages'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': settings.YCLOUD_API_KEY,
    }
    message = f'{agent_name} referred you as a client to Rivo for mortgage assistance. Our team will reach out to you within 30 minutes.'
    payload = {
        'from': settings.YCLOUD_WHATSAPP_NUMBER,
        'to': client_phone,
        'type': 'text',
        'text': {
            'body': message
        },
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f'Client WhatsApp notification failed for {client_phone}: [{response.status_code}] {response.text}')
        else:
            logger.info(f'Client WhatsApp notification sent to {client_phone} (referred by {agent_name})')
        return response.status_code == 200, response.json()
    except requests.RequestException as e:
        logger.error(f'Client WhatsApp notification request failed for {client_phone}: {e}')
        return False, str(e)


def generate_device_token():
    """Generate a unique device token for session persistence."""
    return str(uuid.uuid4())
