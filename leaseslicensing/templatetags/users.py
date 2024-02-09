from django.conf import settings
from django.template import Library

from leaseslicensing import helpers as leaseslicensing_helpers

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
def is_referee(context):
    request = context["request"]
    return leaseslicensing_helpers.is_referee(request)


@register.simple_tag(takes_context=True)
def is_compliance_referee(context):
    request = context["request"]
    return leaseslicensing_helpers.is_compliance_referee(request)


@register.simple_tag(takes_context=True)
def is_assessor(context):
    request = context["request"]
    return leaseslicensing_helpers.is_assessor(request)


@register.simple_tag(takes_context=True)
def is_approver(context):
    request = context["request"]
    return leaseslicensing_helpers.is_approver(request)


@register.simple_tag(takes_context=True)
def is_competitive_process_editor(context):
    request = context["request"]
    return leaseslicensing_helpers.is_competitive_process_editor(request)


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
def dept_support_phone2():
    return settings.DEPT_NAME
