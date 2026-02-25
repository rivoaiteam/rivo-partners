from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from agents.models import Agent
from agents.services import send_inactive_nudge
from config.models import AppConfig


class Command(BaseCommand):
    help = 'Send WhatsApp nudge to agents who have not referred any clients in X days'

    def handle(self, *args, **options):
        inactive_days = AppConfig.get_value('inactive_nudge_days', 7)
        cutoff = timezone.now() - timedelta(days=inactive_days)

        # Active agents who either never submitted or last submitted before cutoff
        agents = Agent.objects.filter(is_active=True).exclude(
            clients__created_at__gte=cutoff,
        ).distinct()

        count = 0
        for agent in agents:
            send_inactive_nudge(agent)
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Sent {count} inactive nudges (threshold: {inactive_days} days)'))
