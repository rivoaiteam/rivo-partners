from django.contrib import admin
from referrals.models import ReferralBonus, NewAgentBonus


@admin.register(ReferralBonus)
class ReferralBonusAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'triggered_by_agent', 'deal_number', 'amount', 'created_at']
    list_filter = ['deal_number', 'created_at']
    search_fields = ['referrer__name', 'referrer__phone', 'triggered_by_agent__name']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['referrer', 'triggered_by_agent', 'triggered_by_client']


@admin.register(NewAgentBonus)
class NewAgentBonusAdmin(admin.ModelAdmin):
    list_display = ['agent', 'deal_number', 'amount', 'created_at']
    list_filter = ['deal_number', 'created_at']
    search_fields = ['agent__name', 'agent__phone']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['agent', 'client']
