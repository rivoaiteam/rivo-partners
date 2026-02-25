import logging
from decimal import Decimal
from config.models import AppConfig
from agents.services import send_referral_bonus_notification, send_milestone_notification
from referrals.models import ReferralBonus, NewAgentBonus

logger = logging.getLogger(__name__)


def process_disbursal_bonuses(client):
    """Called when a client status changes to DISBURSED.
    Handles both referrer bonuses and new agent bonuses."""

    agent = client.source_agent
    logger.info(f'Processing disbursal bonuses: client={client.client_name}, agent={agent.phone}')

    # 1. New Agent Bonus — agent's first N deals
    _process_new_agent_bonus(agent, client)

    # 2. Referrer Bonus — if agent was referred by someone
    if agent.referred_by:
        _process_referrer_bonus(agent.referred_by, agent, client)


def _process_new_agent_bonus(agent, client):
    """Award bonus to agent for their first N disbursed deals."""
    bonus_config = AppConfig.get_value('new_agent_bonuses', [1000, 750, 500])
    existing_count = NewAgentBonus.objects.filter(agent=agent).count()
    if existing_count >= len(bonus_config):
        logger.info(f'New agent bonus skipped: agent={agent.phone} already has {existing_count}/{len(bonus_config)} bonuses')
        return
    deal_number = existing_count + 1

    if deal_number <= len(bonus_config):
        amount = Decimal(str(bonus_config[deal_number - 1]))
        NewAgentBonus.objects.create(
            agent=agent,
            client=client,
            deal_number=deal_number,
            amount=amount,
        )
        logger.info(f'New agent bonus awarded: agent={agent.phone}, deal #{deal_number}, amount={amount}')

    # Milestone check
    total_disbursed = agent.clients.filter(status='DISBURSED').count()
    milestones = AppConfig.get_value('milestone_thresholds', [3, 5, 10, 25, 50])
    if total_disbursed in milestones:
        send_milestone_notification(agent, f'{total_disbursed} deals disbursed')


def _process_referrer_bonus(referrer, triggered_by_agent, client):
    """Award bonus to referrer on first N disbursals across their ENTIRE network."""
    bonus_config = AppConfig.get_value('referrer_bonuses', [500, 500, 1000])
    existing_count = ReferralBonus.objects.filter(referrer=referrer).count()
    if existing_count >= len(bonus_config):
        logger.info(f'Referrer bonus skipped: referrer={referrer.phone} already has {existing_count}/{len(bonus_config)} bonuses')
        return
    deal_number = existing_count + 1

    if deal_number <= len(bonus_config):
        amount = Decimal(str(bonus_config[deal_number - 1]))
        ReferralBonus.objects.create(
            referrer=referrer,
            triggered_by_agent=triggered_by_agent,
            triggered_by_client=client,
            deal_number=deal_number,
            amount=amount,
        )
        logger.info(f'Referrer bonus awarded: referrer={referrer.phone}, triggered_by={triggered_by_agent.phone}, deal #{deal_number}, amount={amount}')
        # Notify referrer via WhatsApp
        send_referral_bonus_notification(referrer, triggered_by_agent, amount, deal_number)
