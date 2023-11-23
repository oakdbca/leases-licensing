from datetime import timedelta

import pytz
from django.conf import settings
from django.template import Library
from django.utils import timezone

from leaseslicensing import helpers as leaseslicensing_helpers
from leaseslicensing.components.main.models import SystemMaintenance

register = Library()


@register.simple_tag(takes_context=True)
def is_leaseslicensing_admin(context):
    # checks if user is an AdminUser
    request = context["request"]
    return leaseslicensing_helpers.is_leaseslicensing_admin(request)


@register.simple_tag(takes_context=True)
def is_internal(context):
    # checks if user is a departmentuser and logged in via single sign-on
    request = context["request"]
    return leaseslicensing_helpers.is_internal(request)


@register.simple_tag(takes_context=True)
def is_assessor(context):
    # checks if user is a departmentuser and logged in via single sign-on
    request = context["request"]
    return leaseslicensing_helpers.is_assessor(request)


@register.simple_tag(takes_context=True)
def is_approver(context):
    # checks if user is a departmentuser and logged in via single sign-on
    request = context["request"]
    return leaseslicensing_helpers.is_approver(request)


@register.simple_tag(takes_context=True)
def is_model_backend(context):
    # Return True if user logged in via single sign-on (or False via social_auth
    # i.e. an external user signing in with a login-token)
    request = context["request"]
    return leaseslicensing_helpers.is_model_backend(request)


@register.simple_tag(takes_context=True)
def is_finance_officer(context):
    request = context["request"]
    return leaseslicensing_helpers.is_finance_officer(request)


@register.simple_tag(takes_context=True)
def is_organisation_access_officer(context):
    request = context["request"]
    return leaseslicensing_helpers.is_organisation_access_officer(request)


@register.simple_tag()
def system_maintenance_due():
    """Returns True (actually a time str), if within <timedelta hours> of system maintenance due datetime"""
    tz = pytz.timezone(settings.TIME_ZONE)
    now = timezone.now()  # returns UTC time
    qs = SystemMaintenance.objects.filter(start_date__gte=now - timedelta(minutes=1))
    if qs:
        obj = qs.earliest("start_date")
        if now >= obj.start_date - timedelta(
            hours=settings.SYSTEM_MAINTENANCE_WARNING
        ) and now <= obj.start_date + timedelta(minutes=1):
            # display time in local timezone
            return "{} - {} (Duration: {} mins)".format(
                obj.start_date.astimezone(tz=tz).ctime(),
                obj.end_date.astimezone(tz=tz).ctime(),
                obj.duration(),
            )
    return False


@register.simple_tag()
def system_maintenance_can_start():
    """Returns True if current datetime is within 1 minute past scheduled start_date"""
    now = timezone.now()  # returns UTC time
    qs = SystemMaintenance.objects.filter(start_date__gte=now - timedelta(minutes=1))
    if qs:
        obj = qs.earliest("start_date")
        if now >= obj.start_date and now <= obj.start_date + timedelta(minutes=1):
            return True
    return False


@register.simple_tag()
def dept_support_phone2():
    return settings.DEPT_NAME
