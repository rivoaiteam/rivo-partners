from rest_framework import serializers
from config.models import AppConfig, HomeBanner


class AppConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppConfig
        fields = ['key', 'value', 'description']


class HomeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeBanner
        fields = ['id', 'title', 'subtitle', 'icon', 'thumbnail', 'cta_text', 'cta_link', 'order']
