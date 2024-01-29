import logging

from django.contrib.auth.signals import user_logged_in
from django.db import transaction

from leaseslicensing.components.proposals.models import ExternalRefereeInvite, Referral

logger = logging.getLogger(__name__)


def process_external_referee_invite(sender, user, request, **kwargs):
    """
    Check if the user logging in has an external referee invite and if so, process it.
    """
    logger.info(
        "user_logged_in_signal running process_external_referee_invite function"
    )
    logger.info("Processing external referee invite for user: %s", user)
    if not ExternalRefereeInvite.objects.filter(
        archived=False, email=user.email, datetime_first_logged_in__isnull=True
    ).exists():
        return

    logger.info("External referee invite found for user: %s", user)

    with transaction.atomic():
        external_referee_invite = ExternalRefereeInvite.objects.get(email=user.email)
        external_referee_invite.datetime_first_logged_in = user.last_login
        logger.info(
            "Saving datetime_first_logged_in for external referee invite: %s",
            external_referee_invite,
        )
        external_referee_invite.save()

        Referral.objects.create(
            proposal=external_referee_invite.proposal,
            referral=user.id,
            sent_by=external_referee_invite.sent_by,
            text=external_referee_invite.invite_text,
            assigned_officer=external_referee_invite.sent_by,
            is_external=True,
        )


user_logged_in.connect(process_external_referee_invite)
