from django.core.management.base import BaseCommand
from config.models import AppConfig


# Initial seed values — admin changes these via Django admin after seeding
SEED_DATA = {
    'commission_min_percent': ('0.45', 'Minimum commission percentage'),
    'commission_max_percent': ('0.60', 'Maximum commission percentage'),
    'avg_payout': ('9000', 'Average payout per referred deal in AED'),
    'referrer_bonuses': ('[500, 500, 1000]', 'Referrer bonus amounts for first 3 disbursals across entire network'),
    'new_agent_bonuses': ('[1000, 750, 500]', 'New agent bonus amounts for their first 3 disbursed deals'),
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
    'inactive_nudge_days': ('7', 'Number of days of inactivity before sending nudge'),
    'welcome_msg': (
        "Hey there! Thanks for verifying. Your Rivo account is now active and ready to go. 🎉\n\nYou can now start helping your clients get their mortgages approved while securing your commissions.\n\nTap here to return to your Rivo dashboard:\n👉 https://partners.rivo.ae",
        'WhatsApp message sent to agent right after OTP verification',
    ),
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
