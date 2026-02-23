import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from config.models import AppConfig, HomeBanner
from config.serializers import HomeBannerSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_config(request):
    """Get all app configuration. Called on every screen load — no caching.
    Values come from DB (AppConfig). If not set in DB, falls back to env vars."""
    config = AppConfig.get_all_config()

    whatsapp_number = os.getenv('YCLOUD_WHATSAPP_NUMBER', '')

    # Defaults from env — only applied if not set in DB
    defaults = {
        'commission_min_percent': float(os.getenv('COMMISSION_MIN_PERCENT', '0.45')),
        'commission_max_percent': float(os.getenv('COMMISSION_MAX_PERCENT', '0.60')),
        'avg_payout': int(os.getenv('AVG_PAYOUT', '9000')),
        'referrer_bonuses': os.getenv('REFERRER_BONUSES', '[500, 500, 1000]'),
        'new_agent_bonuses': os.getenv('NEW_AGENT_BONUSES', '[1000, 750, 500]'),
        'commission_range': os.getenv('COMMISSION_RANGE', '0.45% – 0.60%'),
        'client_whatsapp_msg': os.getenv(
            'CLIENT_WHATSAPP_MSG',
            '{agent_name} referred you as a client to Rivo for mortgage assistance. Our team will reach out to you within 30 minutes.'
        ),
        'referral_share_msg': os.getenv(
            'REFERRAL_SHARE_MSG',
            "Hey, I'm using Rivo to earn mortgage commissions. Join: {url}"
        ),
        'whatsapp_personal': os.getenv('WHATSAPP_PERSONAL_URL', f'https://wa.me/{whatsapp_number.lstrip("+")}'),
        'whatsapp_business': os.getenv('WHATSAPP_BUSINESS_URL', f'https://wa.me/{whatsapp_number.lstrip("+")}'),
        'rivo_join_url': os.getenv('RIVO_JOIN_URL', 'https://partner.rivo.ae/join'),
    }

    # Parse JSON strings for list values
    import json
    for key in ['referrer_bonuses', 'new_agent_bonuses']:
        if key in defaults and isinstance(defaults[key], str):
            try:
                defaults[key] = json.loads(defaults[key])
            except (json.JSONDecodeError, TypeError):
                pass

    for key, default in defaults.items():
        if key not in config:
            config[key] = default

    # Add banners
    banners = HomeBanner.objects.filter(is_active=True)
    config['home_banners'] = HomeBannerSerializer(banners, many=True).data

    return Response(config)
