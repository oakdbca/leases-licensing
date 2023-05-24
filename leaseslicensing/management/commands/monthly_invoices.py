from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run the Monthly Invoices Script - generates invoices per licence/org_applicant for previous month"

    def handle(self, *args, **options):
        raise NotImplementedError("This script is not yet implemented")
