import logging
import requests
from decimal import Decimal

from django.core.management.base import BaseCommand
from clients.models import Client
from referrals.services import process_disbursal_bonuses

logger = logging.getLogger(__name__)

CRM_BASE_URL = 'https://app.rivo.ae'

# Map CRM pipeline_status to our status
STATUS_MAP = {
    'submitted': 'SUBMITTED',
    'contacted': 'CONTACTED',
    'qualified': 'QUALIFIED',
    'approved': 'APPROVED',
    'disbursed': 'DISBURSED',
    'declined': 'DECLINED',
}

# Terminal statuses — no need to sync these anymore
TERMINAL_STATUSES = {'DISBURSED', 'DECLINED'}


class Command(BaseCommand):
    help = 'Sync client statuses from Rivo CRM for all active leads'

    def handle(self, *args, **options):
        clients = Client.objects.filter(
            crm_lead_id__isnull=False,
        ).exclude(
            status__in=TERMINAL_STATUSES,
        )

        total = clients.count()
        updated = 0
        errors = 0

        self.stdout.write(f'Syncing {total} clients from CRM...')

        for client in clients:
            try:
                resp = requests.get(
                    f'{CRM_BASE_URL}/api/leads/status/{client.crm_lead_id}/',
                    timeout=10,
                )
                if resp.status_code != 200:
                    logger.warning(f'CRM returned {resp.status_code} for lead {client.crm_lead_id}')
                    errors += 1
                    continue

                data = resp.json()
                crm_status = data.get('pipeline_status', '')
                new_status = STATUS_MAP.get(crm_status)

                if not new_status:
                    logger.warning(f'Unknown CRM status "{crm_status}" for lead {client.crm_lead_id}')
                    errors += 1
                    continue

                if new_status == client.status:
                    continue

                old_status = client.status
                client.status = new_status

                # Update mortgage amount if CRM has it
                mortgage_amount = data.get('mortgage_amount')
                if mortgage_amount:
                    client.expected_mortgage_amount = Decimal(str(mortgage_amount))
                    # Recalculate estimated commission
                    client.estimated_commission = None

                client.save()
                updated += 1

                # Trigger bonus processing on disbursal
                if new_status == 'DISBURSED' and old_status != 'DISBURSED':
                    process_disbursal_bonuses(client)
                    self.stdout.write(self.style.SUCCESS(
                        f'  DISBURSED: {client.client_name} — bonuses processed'
                    ))
                else:
                    self.stdout.write(f'  {client.client_name}: {old_status} → {new_status}')

            except Exception as e:
                logger.warning(f'Failed to sync lead {client.crm_lead_id}: {e}')
                errors += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. {updated} updated, {errors} errors, {total - updated - errors} unchanged.'
        ))
