from decimal import Decimal
from config.models import AppConfig
from referrals.models import ReferralBonus, NewAgentBonus


def process_disbursal_bonuses(client):
    """Called when a client status changes to DISBURSED.
    Handles both referrer bonuses and new agent bonuses."""

    agent = client.source_agent

    # 1. New Agent Bonus — agent's first 3 deals
    _process_new_agent_bonus(agent, client)

    # 2. Referrer Bonus — if agent was referred by someone
    if agent.referred_by:
        _process_referrer_bonus(agent.referred_by, agent, client)


def _process_new_agent_bonus(agent, client):
    """Award bonus to agent for their first 3 disbursed deals."""
    existing_count = NewAgentBonus.objects.filter(agent=agent).count()
    if existing_count >= 3:
        return  # Already got all 3 bonuses

    bonus_config = AppConfig.get_value('new_agent_bonuses', [1000, 750, 500])
    deal_number = existing_count + 1

    if deal_number <= len(bonus_config):
        amount = Decimal(str(bonus_config[deal_number - 1]))
        NewAgentBonus.objects.create(
            agent=agent,
            client=client,
            deal_number=deal_number,
            amount=amount,
        )


def _process_referrer_bonus(referrer, triggered_by_agent, client):
    """Award bonus to referrer on first 3 disbursals across their ENTIRE network."""
    existing_count = ReferralBonus.objects.filter(referrer=referrer).count()
    if existing_count >= 3:
        return  # Already got all 3 bonuses

    bonus_config = AppConfig.get_value('referrer_bonuses', [500, 500, 1000])
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
