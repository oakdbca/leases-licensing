import logging
import re

from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from ledger_api_client.managed_models import SystemGroup, SystemGroupPermission
from ledger_api_client.utils import get_all_organisation

logger = logging.getLogger(__name__)


def user_ids_in_group(group_name):
    try:
        system_group = SystemGroup.objects.get(name=group_name)
        return system_group.get_system_group_member_ids()
    except SystemGroup.DoesNotExist:
        logger.warn(f"SystemGroup {group_name} does not exist.")
        return []


def belongs_to_by_user_id(user_id, group_name):
    system_group = SystemGroup.objects.filter(name=group_name).first()
    return system_group and user_id in system_group.get_system_group_member_ids()


def emails_list_for_group(group_name):
    sgp = SystemGroupPermission.objects.filter(system_group__name=group_name).only(
        "emailuser"
    )
    return [sgp.emailuser.email for sgp in sgp]


def belongs_to(request, group_name):
    if not request.user.is_authenticated:
        return False
    if request.user.is_superuser:
        return True

    return belongs_to_by_user_id(request.user.id, group_name)


def is_leaseslicensing_admin(request):
    return belongs_to(request, settings.ADMIN_GROUP)


def is_assessor(request):
    return belongs_to(request, settings.GROUP_NAME_ASSESSOR)


def is_approver(request):
    return belongs_to(request, settings.GROUP_NAME_APPROVER)


def is_finance_officer(request):
    return belongs_to(request, settings.GROUP_FINANCE)


def is_referee(request, proposal=None):
    from leaseslicensing.components.proposals.models import Referral
    qs = Referral.objects.filter(referral=request.user.id)
    if proposal:
        qs = qs.filter(proposal=proposal)

    return qs.exists()


def in_dbca_domain(request):
    return request.user.is_staff


def is_in_organisation_contacts(request, organisation):
    """Todo: Convert this to segregated"""
    return request.user.email in organisation.contacts.all().values_list(
        "email", flat=True
    )


def is_department_user(request):
    return request.user.is_authenticated and request.user.is_staff


def is_customer(request):
    return request.user.is_authenticated and not request.user.is_staff


def is_internal(request):
    return is_department_user(request)


def get_leaseslicensing_organisation_ids():
    """Since the organisations of leases and licensing are a small subset of those in ledger
    we can cache the list of organisations to improve performance.

    Todo: Must delete the cache whenever a new organisation is added to the system."""
    from leaseslicensing.components.organisations.models import Organisation

    cache_key = settings.CACHE_KEY_ORGANISATION_IDS
    organisation_ids = cache.get(cache_key)
    if organisation_ids is None:
        organisation_ids = organisation_ids = (
            Organisation.objects.all().values_list("organisation", flat=True).distinct()
        )
        cache.set(cache_key, organisation_ids, settings.CACHE_TIMEOUT_2_HOURS)
    logger.debug(f"{cache_key}:{organisation_ids}")
    return organisation_ids


def get_leaseslicensing_organisations():
    """Since the organisations of leases and licensing are a small subset of those in ledger
    we can cache the list of organisations to improve performance."""
    cache_key = settings.CACHE_KEY_ORGANISATIONS
    organisations = cache.get(cache_key)
    if organisations is None:
        leases_organisation_ids = get_leaseslicensing_organisation_ids()
        all_organisations_response = get_all_organisation()
        all_organisations = all_organisations_response["data"]
        organisations = []
        for org in all_organisations:
            if org["organisation_id"] in leases_organisation_ids:
                organisations.append(org)
    cache.set(cache_key, organisations, settings.CACHE_TIMEOUT_2_HOURS)
    logger.debug(f"{cache_key}:{organisations}")
    return organisations


def get_leaseslicensing_external_emailuser_ids():
    """Since the users of leases and licensing are a small subset of those in ledger
    we can cache the list of users to improve performance.

    Todo:   Must delete the cache whenever a new user is added to the system.
            Must add all possible user ids that can appear in the search results.
    """
    # Avoid circular imports
    from leaseslicensing.components.approvals.models import Approval
    from leaseslicensing.components.compliances.models import Compliance
    from leaseslicensing.components.proposals.models import Proposal

    cache_key = settings.CACHE_KEY_USER_IDS
    user_ids = cache.get(cache_key)
    if user_ids is None:
        submitters = list(
            Proposal.objects.all().values_list("submitter", flat=True).distinct()
        )
        approval_submitters = list(
            Approval.objects.all().values_list("submitter", flat=True).distinct()
        )
        compliance_submitters = list(
            Compliance.objects.all().values_list("submitter", flat=True).distinct()
        )
        # There are almost certainly other users that should be included here.

        # combine lists and remove duplicates
        user_ids = list(set(submitters + approval_submitters + compliance_submitters))
        cache.set(cache_key, user_ids, settings.CACHE_TIMEOUT_2_HOURS)
    logger.debug(f"{cache_key}:{user_ids}")
    return user_ids


def get_instance_identifier(instance):
    """Checks the instance for the attributes specified in settings"""
    for field in settings.ACTION_LOGGING_IDENTIFIER_FIELDS:
        if hasattr(instance, field):
            return getattr(instance, field)
    raise AttributeError(
        f"Model instance has no valid identifier to use for logging. Tried: {settings.ACTION_LOGGING_IDENTIFIER_FIELDS}"
    )


def get_lodgement_number_prefixes():
    """Returns the prefixes of the models that have a lodgement_number field"""
    cache_key = settings.CACHE_KEY_LODGEMENT_NUMBER_PREFIXES
    prefixes = cache.get(cache_key)
    if prefixes is None:
        leaseslicensing = apps.get_app_config("leaseslicensing")
        prefixes = {}
        for model_string in leaseslicensing.models:
            model = apps.get_model("leaseslicensing", model_string)
            if (hasattr(model, "lodgement_number")) and (
                hasattr(model, "MODEL_PREFIX")
            ):
                prefixes[model.MODEL_PREFIX] = model
        cache.set(cache_key, prefixes, settings.CACHE_TIMEOUT_2_HOURS)
    return prefixes


def get_model_by_lodgement_number_prefix(prefix):
    """Returns the model class for the prefix"""
    return get_lodgement_number_prefixes()[prefix]


def get_model_by_lodgement_number(lodgement_number):
    """Returns the model class for the lodgement number"""
    lodgment_number = re.search("([A-Z]+)([0-9]+)", lodgement_number)
    if not lodgment_number:
        raise ValueError(
            "A valid lodgement number starts with one or more capital letters followed by a series of digits."
        )

    lodgement_number_prefix = lodgment_number.group(1)
    return get_model_by_lodgement_number_prefix(lodgement_number_prefix)
