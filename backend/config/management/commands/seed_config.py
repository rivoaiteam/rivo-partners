from django.core.management.base import BaseCommand
from config.models import AppConfig


# Initial seed values — admin changes these via Django admin after seeding
SEED_DATA = {
    'commission_min_percent': ('0.45', 'Minimum commission percentage'),
    'commission_max_percent': ('0.60', 'Maximum commission percentage'),
    'avg_payout': ('9000', 'Average payout per referred deal in AED'),
    'referrer_bonuses': ('[500, 500, 1000]', 'Referrer bonus amounts for first 3 disbursals across entire network'),
    'new_agent_bonuses': ('[1000, 750, 500]', 'New agent bonus amounts for their first 3 disbursed deals'),
    'client_whatsapp_msg': (
        '{agent_name} referred you as a client to Rivo for mortgage assistance. Our team will reach out to you within 30 minutes.',
        'WhatsApp message sent to referred client',
    ),
    'referral_share_msg': (
        "Hey, I'm using Rivo to earn mortgage commissions. Join: {url}",
        'Pre-filled message for agent referral share sheet',
    ),
    'whatsapp_personal': ('https://wa.me/971545079577', 'WhatsApp personal deep link URL'),
    'whatsapp_business': ('https://wa.me/971545079577', 'WhatsApp Business deep link URL'),
    'referral_signup_msg': (
        'Great news! {agent_name} just joined Rivo using your referral link. You earn bonuses when their deals get disbursed.',
        'WhatsApp message sent to referrer when their referred agent signs up',
    ),
    'referral_bonus_msg': (
        "You earned AED {amount} referral bonus! {agent_name}'s deal #{deal_number} was disbursed. Keep growing your network!",
        'WhatsApp message sent to referrer when they earn a referral bonus',
    ),
    'inactive_nudge_msg': (
        "Hey {agent_name}, you haven't submitted any clients recently. Refer a mortgage client today and earn commissions! Open Rivo Partners: https://partners.rivo.ae",
        'WhatsApp nudge sent to agents who have not referred clients recently',
    ),
    'milestone_msg': (
        "Congratulations {agent_name}! You've hit a milestone: {milestone}. Keep up the great work!",
        'WhatsApp message sent when agent reaches a milestone',
    ),
    'inactive_nudge_days': ('7', 'Number of days of inactivity before sending nudge'),
    'milestone_thresholds': ('[3, 5, 10, 25, 50]', 'List of deal counts that trigger milestone notifications'),
}


class Command(BaseCommand):
    help = 'Seed default app configuration values into AppConfig table'

    def handle(self, *args, **options):
        created_count = 0
        for key, (value, description) in SEED_DATA.items():
            obj, created = AppConfig.objects.get_or_create(
                key=key,
                defaults={'value': value, 'description': description},
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {key}'))
            else:
                self.stdout.write(f'  Exists: {key}')

        self.stdout.write(self.style.SUCCESS(f'\nDone. {created_count} new config entries created.'))
