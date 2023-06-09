from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Run the Invoice Payment Due Notification Script - generates emails to licence holder and "
        "assessor for all invoices that are due today, and not yet paid"
    )

    def handle(self, *args, **options):
        raise NotImplementedError("This script is not yet implemented")
