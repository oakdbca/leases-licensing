import logging

from django.conf import settings
from django.core.cache import cache
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from leaseslicensing.components.main.decorators import (
    basic_exception_handler,
    user_notexists_exception_handler,
)

logger = logging.getLogger(__name__)


@basic_exception_handler
@user_notexists_exception_handler
def retrieve_email_user(email_user_id):
    cache_key = settings.CACHE_KEY_LEDGER_EMAIL_USER.format(email_user_id)
    email_user = cache.get(cache_key)
    if email_user is None:
        email_user = EmailUser.objects.get(id=email_user_id)
        logger.debug(f"{cache_key}:{email_user}")
        # Todo: A per request cache would be best here
        cache.set(cache_key, email_user, settings.CACHE_TIMEOUT_1_MINUTE)
    return email_user
