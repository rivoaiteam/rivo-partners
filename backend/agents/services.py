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


def _send_whatsapp_template(phone, template_name, parameters=None):
    """Send a WhatsApp template message via YCloud (works outside 24h window)."""
    url = 'https://api.ycloud.com/v2/whatsapp/messages'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': settings.YCLOUD_API_KEY,
    }
    template = {
        'name': template_name,
        'language': {'code': 'en'},
    }
    if parameters:
        template['components'] = [{
            'type': 'body',
            'parameters': [{'type': 'text', 'text': str(p)} for p in parameters],
        }]
    payload = {
        'from': settings.YCLOUD_WHATSAPP_NUMBER,
        'to': phone,
        'type': 'template',
        'template': template,
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f'WhatsApp template send failed to {phone}: template={template_name} [{response.status_code}] {response.text}')
        else:
            logger.info(f'WhatsApp template sent to {phone}: template={template_name}')
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f'WhatsApp template request failed to {phone}: {e}')
        return False


def send_verification_reply(phone, code, is_returning_user=False):
    """Send WhatsApp reply after verification with link back to the app.
    Uses welcome_back_msg for returning users, welcome_msg for new users.
    Uses plain text (within 24h customer service window)."""
    url = f'https://partners.rivo.ae/whatsapp-verify?code={code}'
    config_key = 'welcome_back_msg' if is_returning_user else 'welcome_msg'
    try:
        template = AppConfig.objects.get(key=config_key).value
    except AppConfig.DoesNotExist:
        # Fall back to welcome_msg if welcome_back_msg doesn't exist yet
        try:
            template = AppConfig.objects.get(key='welcome_msg').value
        except AppConfig.DoesNotExist:
            logger.warning('welcome_msg not found in AppConfig, skipping verification reply')
            return False
    message = template.replace('{url}', url)
    return _send_whatsapp(phone, message)


def send_referral_signup_notification(referrer, new_agent):
    """Notify referrer when their referred agent signs up.
    Template: referral_signup_msg — {{1}} = agent_name"""
    agent_name = new_agent.name or new_agent.phone
    return _send_whatsapp_template(referrer.phone, 'referral_signup_msg', [agent_name])


def send_client_whatsapp_notification(client_phone, agent_name, client_name):
    """Send WhatsApp notification to referred client via YCloud template.
    Template: client_whatsapp_msg — {{1}} = agent_name"""
    return _send_whatsapp_template(client_phone, 'client_whatsapp_msg', [agent_name])


def send_referral_bonus_notification(referrer, agent, bonus_amount, deal_number):
    """Notify referrer when they earn a referral bonus via YCloud template.
    Template: referral_bonus_msg — {{1}} = amount, {{2}} = agent_name, {{3}} = deal_number"""
    agent_name = agent.name or agent.phone
    return _send_whatsapp_template(referrer.phone, 'referral_bonus_msg', [bonus_amount, agent_name, deal_number])


def send_client_status_update_notification(agent, client_name, new_status):
    """Notify the source agent when their referred client's status changes.
    Template: referrer_status_update_1 — {{1}} = agent_name, {{2}} = client_name, {{3}} = status"""
    STATUS_LABELS = {
        'SUBMITTED': 'submitted',
        'CONTACTED': 'now being contacted by Rivo',
        'QUALIFIED': 'qualified for a mortgage',
        'SUBMITTED_TO_BANK': 'now submitted to the bank',
        'PREAPPROVED': 'now pre-approved by the bank',
        'FOL_RECEIVED': 'now at the offer letter stage',
        'DISBURSED': 'now disbursed',
        'DECLINED': 'declined',
    }
    agent_name = agent.name or 'Partner'
    status_label = STATUS_LABELS.get(new_status, new_status)
    return _send_whatsapp_template(agent.phone, 'referrer_status_update_1', [agent_name, client_name, status_label])


def send_inactive_nudge(agent):
    """Send nudge to agent who hasn't referred in X days via YCloud template.
    Template: inactive_nudge_msg — {{1}} = agent_name"""
    agent_name = agent.name or 'Partner'
    return _send_whatsapp_template(agent.phone, 'inactive_nudge_msg', [agent_name])


def generate_device_token():
    """Generate a unique device token for session persistence."""
    return str(uuid.uuid4())
