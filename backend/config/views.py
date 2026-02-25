import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from config.models import AppConfig, HomeBanner
from config.serializers import HomeBannerSerializer


# Hardcoded initial defaults — admin overrides these via Django admin (AppConfig table)
DEFAULTS = {
    'commission_min_percent': 0.45,
    'commission_max_percent': 0.60,
    'avg_payout': 9000,
    'referrer_bonuses': [500, 500, 1000],
    'client_whatsapp_msg': '{agent_name} referred you as a client to Rivo for mortgage assistance. Our team will reach out to you within 30 minutes.',
    'referral_share_msg': "Hey, I'm using Rivo to earn mortgage commissions. Join: {url}",
    'whatsapp_personal': 'https://wa.me/971545079577',
    'whatsapp_business': 'https://wa.me/971545079577',
}


@api_view(['GET'])
@permission_classes([AllowAny])
def get_config(request):
    """Get all app configuration. Values come from DB (AppConfig).
    Falls back to hardcoded defaults if not set in DB."""
    config = AppConfig.get_all_config()

    for key, default in DEFAULTS.items():
        if key not in config:
            config[key] = default

    # Add banners
    banners = HomeBanner.objects.filter(is_active=True)
    config['home_banners'] = HomeBannerSerializer(banners, many=True).data

    return Response(config)
