from django.conf import settings

from leaseslicensing.components.organisations.models import Organisation
from leaseslicensing.settings import template_group, template_title


def leaseslicensing_url(request):
    organisations_user_can_admin = Organisation.organisations_user_can_admin(
        request.user.id
    )
    return {
        "GIS_SERVER_URL": settings.GIS_SERVER_URL,
        "template_group": template_group,
        "template_title": template_title,
        "organisations_user_can_admin": organisations_user_can_admin,
        "build_tag": settings.BUILD_TAG,
        "LEDGER_UI_URL": settings.LEDGER_UI_URL,
        "PAYMENT_SYSTEM_PREFIX": settings.PAYMENT_SYSTEM_PREFIX,
        "app_build_url": settings.DEV_APP_BUILD_URL,
    }
