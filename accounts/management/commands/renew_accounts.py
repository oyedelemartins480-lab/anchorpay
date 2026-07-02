from django.core.management.base import BaseCommand
from accounts.models import NombaAccount
from accounts.nomba_client import renew_account_if_needed


class Command(BaseCommand):
    help = "Checks all active Nomba accounts and renews any close to expiry"

    def handle(self, *args, **options):
        active_accounts = NombaAccount.objects.filter(is_active=True)
        renewed_count = 0

        for account in active_accounts:
            result = renew_account_if_needed(account)
            if result is not None:
                renewed_count += 1
                self.stdout.write(
                    f"Renewed account for {account.persistent_account.customer_name}"
                )

        self.stdout.write(
            self.style.SUCCESS(f"Done. Renewed {renewed_count} account(s).")
        )