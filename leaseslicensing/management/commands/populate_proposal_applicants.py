""" Maybe useful for populating proposal applicants from ind_applicants """
import json
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from ledger_api_client import utils as ledger_api_client_utils
from ledger_api_client.api import get_account_details
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from leaseslicensing.components.proposals.models import Proposal, ProposalApplicant

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Create a proposal applicant for each ind_applicant in the system
    """

    help = "Create a proposal applicant for each ind_applicant in the system"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            logger.error(
                "This command can only be run in DEBUG mode (Only run this if you know what you're doing)"
            )
            return

        address_details = {}
        for proposal in Proposal.objects.all():
            ind_applicant = proposal.ind_applicant
            if not ind_applicant:
                continue

            email_user = EmailUser.objects.get(id=ind_applicant)
            # Json parse
            if email_user.id not in address_details:
                applicant_details = {
                    k: v
                    for k, v in email_user.__dict__.items()
                    if k
                    in [
                        "email",
                        "first_name",
                        "last_name",
                        "dob",
                        "phone_number",
                        "mobile_number",
                        "postal_same_as_residential",
                    ]
                }

                fake_request = ledger_api_client_utils.FakeRequestSessionObj()
                a_super_user = EmailUser.objects.filter(is_superuser=True).first()
                fake_request.user = a_super_user
                account_details = json.loads(
                    get_account_details(fake_request, str(a_super_user.id)).content
                )["data"]["residential_address"]

                applicant_details["residential_line1"] = account_details["line1"]
                applicant_details["residential_line2"] = account_details["line2"]
                applicant_details["residential_line3"] = account_details["line3"]
                applicant_details["residential_locality"] = account_details["locality"]
                applicant_details["residential_state"] = account_details["state"]
                applicant_details["residential_country"] = account_details["country"]
                applicant_details["residential_postcode"] = account_details["postcode"]
                address_details[email_user.id] = applicant_details

            # Update proposal applicant
            ProposalApplicant.objects.update_or_create(
                proposal=proposal, **applicant_details
            )
