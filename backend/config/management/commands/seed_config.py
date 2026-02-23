import os
import json
from django.core.management.base import BaseCommand
from config.models import AppConfig


class Command(BaseCommand):
    help = 'Seed default app configuration values from env vars'

    def handle(self, *args, **options):
        defaults = {
            'commission_min_percent': {
                'value': os.getenv('COMMISSION_MIN_PERCENT', '0.45'),
                'description': 'Minimum commission percentage',
            },
            'commission_max_percent': {
                'value': os.getenv('COMMISSION_MAX_PERCENT', '0.60'),
                'description': 'Maximum commission percentage',
            },
            'avg_payout': {
                'value': os.getenv('AVG_PAYOUT', '9000'),
                'description': 'Average payout per referred deal in AED',
            },
            'referrer_bonuses': {
                'value': os.getenv('REFERRER_BONUSES', '[500, 500, 1000]'),
                'description': 'Referrer bonus amounts for first 3 disbursals across entire network',
            },
            'new_agent_bonuses': {
                'value': os.getenv('NEW_AGENT_BONUSES', '[1000, 750, 500]'),
                'description': 'New agent bonus amounts for their first 3 deals',
            },
            'commission_range': {
                'value': json.dumps(os.getenv('COMMISSION_RANGE', '0.45% – 0.60%')),
                'description': 'Display string for commission range',
            },
            'client_whatsapp_msg': {
                'value': json.dumps(os.getenv(
                    'CLIENT_WHATSAPP_MSG',
                    '{agent_name} referred you as a client to Rivo for mortgage assistance. Our team will reach out to you within 30 minutes.'
                )),
                'description': 'WhatsApp message sent to referred client',
            },
            'referral_share_msg': {
                'value': json.dumps(os.getenv(
                    'REFERRAL_SHARE_MSG',
                    "Hey, I'm using Rivo to earn mortgage commissions. Join: {url}"
                )),
                'description': 'Pre-filled message for agent referral share sheet',
            },
            'whatsapp_personal': {
                'value': json.dumps(os.getenv('WHATSAPP_PERSONAL_URL', 'https://wa.me/971545079577')),
                'description': 'WhatsApp personal deep link URL',
            },
            'whatsapp_business': {
                'value': json.dumps(os.getenv('WHATSAPP_BUSINESS_URL', 'https://wa.me/971545079577')),
                'description': 'WhatsApp Business deep link URL',
            },
            'rivo_join_url': {
                'value': json.dumps(os.getenv('RIVO_JOIN_URL', 'https://partner.rivo.ae/join')),
                'description': 'Base URL for agent referral join links',
            },
        }

        created_count = 0
        for key, data in defaults.items():
            obj, created = AppConfig.objects.get_or_create(
                key=key,
                defaults={
                    'value': data['value'],
                    'description': data['description'],
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {key}'))
            else:
                self.stdout.write(f'  Exists: {key}')

        self.stdout.write(self.style.SUCCESS(f'\nDone. {created_count} new config entries created.'))
