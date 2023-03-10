from django.conf import settings

from leaseslicensing.settings import template_group, template_title


def leaseslicensing_url(request):
    return {
        "KMI_SERVER_URL": settings.KMI_SERVER_URL,
        "template_group": template_group,
        "template_title": template_title,
        "build_tag": settings.BUILD_TAG,
        "app_build_url": settings.DEV_APP_BUILD_URL,
    }
