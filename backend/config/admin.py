from django.contrib import admin
from config.models import AppConfig, HomeBanner


@admin.register(AppConfig)
class AppConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description', 'updated_at']
    search_fields = ['key', 'description']
    readonly_fields = ['updated_at']


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'cta_text', 'is_active', 'order', 'updated_at']
    list_filter = ['is_active']
    list_editable = ['is_active', 'order']
    search_fields = ['title', 'subtitle']
    readonly_fields = ['created_at', 'updated_at']
