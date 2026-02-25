import logging
import requests
import uuid
from django.conf import settings
from config.models import AppConfig

logger = logging.getLogger(__name__)


def _send_whatsapp(phone, message):
    """Send a WhatsApp message via YCloud."""
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


def send_client_whatsapp_notification(client_phone, agent_name, client_name):
    """Send WhatsApp notification to referred client. Message from config."""
    template = AppConfig.get_value(
        'client_whatsapp_msg',
        '{agent_name} referred you as a client to Rivo for mortgage assistance. Our team will reach out to you within 30 minutes.'
    )
    message = template.replace('{agent_name}', agent_name).replace('{client_name}', client_name)
    return _send_whatsapp(client_phone, message)


def send_referral_signup_notification(referrer, new_agent):
    """Notify referrer when their referred agent signs up (Case 4)."""
    template = AppConfig.get_value(
        'referral_signup_msg',
        'Great news! {agent_name} just joined Rivo using your referral link. You earn bonuses when their deals get disbursed.'
    )
    agent_name = new_agent.name or new_agent.phone
    message = template.replace('{agent_name}', agent_name)
    return _send_whatsapp(referrer.phone, message)


def send_referral_bonus_notification(referrer, agent, bonus_amount, deal_number):
    """Notify referrer when they earn a referral bonus (Case 5)."""
    template = AppConfig.get_value(
        'referral_bonus_msg',
        'You earned AED {amount} referral bonus! {agent_name}\'s deal #{deal_number} was disbursed. Keep growing your network!'
    )
    agent_name = agent.name or agent.phone
    message = (template
               .replace('{amount}', str(bonus_amount))
               .replace('{agent_name}', agent_name)
               .replace('{deal_number}', str(deal_number)))
    return _send_whatsapp(referrer.phone, message)


def send_inactive_nudge(agent):
    """Send nudge to agent who hasn't referred in X days (Case 6)."""
    template = AppConfig.get_value(
        'inactive_nudge_msg',
        'Hey {agent_name}, you haven\'t submitted any clients recently. Refer a mortgage client today and earn commissions! Open Rivo Partners: https://partners.rivo.ae'
    )
    agent_name = agent.name or 'Partner'
    message = template.replace('{agent_name}', agent_name)
    return _send_whatsapp(agent.phone, message)


def send_milestone_notification(agent, milestone):
    """Send milestone notification (Case 7)."""
    template = AppConfig.get_value(
        'milestone_msg',
        'Congratulations {agent_name}! You\'ve hit a milestone: {milestone}. Keep up the great work!'
    )
    agent_name = agent.name or 'Partner'
    message = template.replace('{agent_name}', agent_name).replace('{milestone}', milestone)
    return _send_whatsapp(agent.phone, message)


def generate_device_token():
    """Generate a unique device token for session persistence."""
    return str(uuid.uuid4())
