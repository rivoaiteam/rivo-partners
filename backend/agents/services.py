import logging
import requests
import uuid
from django.conf import settings
from config.models import AppConfig

logger = logging.getLogger(__name__)


def _send_whatsapp(phone, message):
    """Send a WhatsApp message via YCloud (plain text — works within 24h window)."""
    url = 'https://api.ycloud.com/v2/whatsapp/messages'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': settings.YCLOUD_API_KEY,
    }
    payload = {
        'from': settings.YCLOUD_WHATSAPP_NUMBER,
        'to': phone,
        'type': 'text',
        'text': {'body': message},
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f'WhatsApp send failed to {phone}: [{response.status_code}] {response.text}')
        else:
            logger.info(f'WhatsApp sent to {phone}: {message[:50]}...')
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f'WhatsApp request failed to {phone}: {e}')
        return False


def send_referral_signup_notification(referrer, new_agent):
    """Notify referrer when their referred agent signs up (Case 4).
    Works as plain text since referrer has open 24h conversation window."""
    template = AppConfig.get_value(
        'referral_signup_msg',
        'Great news! {agent_name} just joined Rivo using your referral link. You earn bonuses when their deals get disbursed.'
    )
    agent_name = new_agent.name or new_agent.phone
    message = template.replace('{agent_name}', agent_name)
    return _send_whatsapp(referrer.phone, message)


def generate_device_token():
    """Generate a unique device token for session persistence."""
    return str(uuid.uuid4())
