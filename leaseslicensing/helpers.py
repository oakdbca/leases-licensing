from __future__ import unicode_literals
from ledger_api_client.ledger_models import EmailUserRO as EmailUser, EmailUserRO
from ledger_api_client.managed_models import SystemGroup
from django.conf import settings
from django.core.cache import cache
from django.db.models import Case, When

import logging
import functools

from leaseslicensing.settings import GROUP_NAME_ASSESSOR, GROUP_NAME_APPROVER
from leaseslicensing.components.main.decorators import basic_exception_handler
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework import serializers

logger = logging.getLogger(__name__)


def belongs_to(user, group_name):
    """
    Check if the user belongs to the given group.
    :param user:
    :param group_name:
    :return:
    """
    # import ipdb; ipdb.set_trace()
    belongs_to_value = cache.get(
        "User-belongs_to" + str(user.id) + "group_name:" + group_name
    )
    if belongs_to_value:
        print(
            "From Cache - User-belongs_to" + str(user.id) + "group_name:" + group_name
        )
    if belongs_to_value is None:
        belongs_to_value = user.groups().filter(name=group_name).exists()
        cache.set(
            "User-belongs_to" + str(user.id) + "group_name:" + group_name,
            belongs_to_value,
            3600,
        )
    return belongs_to_value

    # return user.groups.filter(name=group_name).exists()


# def is_model_backend(request):
#    # Return True if user logged in via single sign-on (i.e. an internal)
#    return 'ModelBackend' in request.session.get('_auth_user_backend')
#
# def is_email_auth_backend(request):
#    # Return True if user logged in via social_auth (i.e. an external user signing in with a login-token)
#    return 'EmailAuth' in request.session.get('_auth_user_backend')


def is_leaseslicensing_admin(request):
    # logger.info('settings.ADMIN_GROUP: {}'.format(settings.ADMIN_GROUP))
    return request.user.is_authenticated and (
        request.user.is_superuser or belongs_to(request.user, settings.ADMIN_GROUP)
    )


def is_assessor(user_id):
    if isinstance(user_id, EmailUser) or isinstance(user_id, EmailUserRO):
        user_id = user_id.id
    assessor_group = SystemGroup.objects.get(name=GROUP_NAME_ASSESSOR)
    return True if user_id in assessor_group.get_system_group_member_ids() else False


def is_approver(user_id):
    if isinstance(user_id, EmailUser) or isinstance(user_id, EmailUserRO):
        user_id = user_id.id
    assessor_group = SystemGroup.objects.get(name=GROUP_NAME_APPROVER)
    return True if user_id in assessor_group.get_system_group_member_ids() else False


def in_dbca_domain(request):
    return request.user.is_staff


#    #import ipdb; ipdb.set_trace()
#    user = request.user
#    domain = user.email.split('@')[1]
#    if domain in settings.DEPT_DOMAINS:
#        if not user.is_staff:
#            # hack to reset department user to is_staff==True, if the user logged in externally (external departmentUser login defaults to is_staff=False)
#            user.is_staff = True
#            user.save()
#        return True
#    return False


def is_in_organisation_contacts(request, organisation):
    return request.user.email in organisation.contacts.all().values_list(
        "email", flat=True
    )


def is_departmentUser(user):
    # return request.user.is_authenticated and is_model_backend(request) and in_dbca_domain(request)
    try:
        return user.is_authenticated and user.is_staff
    except AttributeError as e:
        #  user is probably Request type
        return user.user.is_authenticated and user.user.is_staff
    except Exception as e:
        raise


def is_customer(user):
    # return request.user.is_authenticated and is_email_auth_backend(request)
    try:
        return user.is_authenticated and not user.is_staff
    except AttributeError as e:
        # user is probably Request type
        return user.user.is_authenticated and not user.user.is_staff
    except Exception as e:
        raise


def is_internal(request):
    return is_departmentUser(request)


def get_all_officers():
    return EmailUser.objects.filter(groups__name="Commercial Operator Admin")


class TableSearchOrderHelper(DatatablesFilterBackend):

    LEDGER_LOOKUP_FIELDS = []
    SPECIAL_ORDERING_FIELDS = []


    def __init__(self, model, **kwargs):
        """Constructor

            Args:
                model (models.Model): The table's model class
                ledger_lookup_fields (list, optional): The field in the model that functions as the foreign key to ledger
                special_ordering_fields (list, optional); Fields that are not part of the model and need special ordering treatment
        """

        self.model = model
        self.LEDGER_LOOKUP_FIELDS = kwargs.get("ledger_lookup_fields", ["submitter"])
        self.SPECIAL_ORDERING_FIELDS = kwargs.get("special_ordering_fields", [])


    @basic_exception_handler
    def split_list_to_dict(self, list_to_split):
        result_dict = {}
        for item in list_to_split:
            if '.' not in item:
                continue
            key, value = item.split('.')
            result_dict.setdefault(key, []).append(value)
        return result_dict


    @basic_exception_handler
    def rgetattr(self, obj, attr, *args):
        def _getattr(obj, attr):
            if isinstance(obj, dict):
                return obj.get(attr, None)
            else:
                return getattr(obj, attr, *args)
        return functools.reduce(_getattr, [obj] + attr.split('.'))


    @basic_exception_handler
    def search_attrs(self, search_value, attributes, model):
        # ledger foreign key attributes in leases (e.g. submitter)
        _ledger_attrs = {}
        # First search leases attributes and store ledger foreign keys for later
        for attribute in attributes:
            _attr_parts = attribute.split(".")
            # Handle the top-level attribute being a "foreign key" to ledger
            if _attr_parts[0] in self.LEDGER_LOOKUP_FIELDS:
                # Add ledger attribute fields to a dict first, as they are more expensive to search for (segregated database)
                if _attr_parts[0] not in _ledger_attrs:
                    # Create ledger attribute if not exists
                    _ledger_attrs[_attr_parts[0]] = []
                _ledger_attrs[_attr_parts[0]].append(".".join(_attr_parts[1:]))

            else:
                # Retrieve the attribute value from this model
                attribute_value = str(self.rgetattr(model, attribute)).lower()
                # Handle processing status' attribute value being stored in snake_case instead of a written form
                if attribute == "processing_status":
                    choices = [c for c in model.PROCESSING_STATUS_CHOICES if c[0] == attribute_value]
                    if len(choices) > 0:
                        attribute_value = choices[0][1].lower()

                if search_value in attribute_value:
                    logger.info(f"Found `{search_value}` in LEASES attribute {attribute}: {attribute_value}")
                    return True

        if _ledger_attrs:
            for attribute in _ledger_attrs:
                _fk = self.rgetattr(model, attribute) # ledger foreign key
                if _fk is None:
                    # No valid foreign key value
                    logger.warn(f"Attribute `{attribute}` in model has None-type foreign key")
                    return False
                # Check that only one entry is returned
                ledger = EmailUser.objects.filter(pk=_fk).values(*_ledger_attrs[attribute])
                if len(ledger) == 1:
                    ledger = ledger[0]
                else:
                    raise serializers.ValidationError(f"There must only be one email user in ledger. Received {ledger}")

                if any(search_value in str(self.rgetattr(ledger, a)).lower() for a in _ledger_attrs[attribute]):
                    logger.info(f"Found `{search_value}` in LEDGER attribute {attribute}: {str(self.rgetattr(model, attribute))}")
                    return True

        # logger.info(f"Could not find `{search_value}` in model")
        return False


    @basic_exception_handler
    def get_ordering(self, request, view, fields):
        """ Overwrite `filters::get_ordering` fn
            Returns list of order literals if provided in the form of
            "field_name1, field_name2" or "key__field_name1, key__field_name2"
        """

        ordering = []
        for field, dir_ in self.get_ordering_fields(request, view, fields):
            ordering.append(",".join(['%s%s' % (
                '-' if dir_ == 'desc' else '',
                    f
                ) for f in field["name"]])
            )
        self.append_additional_ordering(ordering, view)
        return ordering

    @basic_exception_handler
    def search_order_queryset(self, request, queryset, view, **kwargs):
        """"""

        proposal_list = []
        datatables_query = self.parse_datatables_query(request, view)
        search_value = datatables_query["search_value"].lower().strip()
        # Fields to search / order for
        datatables_search_query = [q for q in datatables_query["fields"] if q["searchable"]==True]
        datatables_search_attributes = [a.replace('__', '.') for s in datatables_search_query for a in s["name"]]
        # Require at least two characters before searching
        if len(search_value) > 1:
            proposal_list = list(filter(lambda proposal: self.search_attrs(search_value, datatables_search_attributes, proposal), list(queryset)))
        else:
            proposal_list = list(queryset)

        # Ordering
        fields = self.get_fields(request)
        orderings = self.get_ordering(request, view, fields)
        orderings_dotnot = [f.replace("__", ".") for f in orderings[0].split(",")]
        # Order fields that are not part of this model
        if any([sublist.replace("-", "") in self.SPECIAL_ORDERING_FIELDS for inner in orderings_dotnot for sublist in inner.split(".")]):
            ordering = ",".join(orderings_dotnot)
            # Ascending or descending
            reverse = ordering.startswith("-")
            # Handle ordering by ledger field
            if ordering.replace("-", "").split(".")[0] in self.LEDGER_LOOKUP_FIELDS:
                # Transform a list dot-notation strings (key.field) to a dictionary in the form of {key:[fields]}
                ord_dict = self.split_list_to_dict(orderings_dotnot)
                # Ledger "foreign keys" in model
                model_fpks = [getattr(model, attr.replace("-", "")) for model in proposal_list for attr in list(ord_dict.keys())]
                # Get a distinct list of ledger keys on which to order
                ledger_pks = list(set(model_fpks))
                # Get a list of ledger fields to order for
                ledger_orderings = [inner for outer in list(ord_dict.values()) for inner in outer]
                # Query ledger
                ledger = EmailUser.objects.filter(pk__in=ledger_pks).order_by(*ledger_orderings)
                # List of ordered keys in ledger
                ledger_pk_list = [l.pk for l in list(ledger)]
                # Dictionary of counted ledger "foreign keys" in model
                model_fpks_cnt = {pk:model_fpks.count(pk) for pk in ledger_pks}
                # An expanded list of ledger "foreign keys"
                model_fpks_sort = [inner for outer in [[p]*model_fpks_cnt[p] for p in ledger_pk_list] for inner in outer]
                # Handle None-type ledger "foreign key", prepend or append the respective amount of None
                if reverse:
                    model_fpks_sort = [None]*model_fpks_cnt[None] + model_fpks_sort
                else:
                    model_fpks_sort = model_fpks_sort + [None]*model_fpks_cnt[None]

                if len(model_fpks_sort) != len(proposal_list):
                    raise serializers.ValidationError("`model_attr_sort` does not match length of QuerySet")

                # Get a list of keys
                pk_list = [l.pk for l in proposal_list]
                # Preserve the order of the list of keys
                fpk_attr = list(ord_dict.keys())[0].replace("-", "")
                preserved_order = Case(*[When(**{fpk_attr:fpk, "then":pos}) for pos, fpk in enumerate(model_fpks_sort)])
            else:
                # Order list of Proposals
                proposal_list = sorted(proposal_list, key=lambda p: self.rgetattr(p, ordering.replace("-", "")), reverse=reverse)
                # Get a list of keys
                pk_list = [l.pk for l in proposal_list]
                # Preserve the order of the list of keys
                preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])

            # Convert back to Proposal Queryset using the sorting of `proposal_list`
            queryset = self.model.objects.filter(pk__in=pk_list).distinct().order_by(preserved_order)
        else:
            # Convert back to Proposal Queryset
            pk_list = [l.pk for l in proposal_list]
            queryset = self.model.objects.filter(pk__in=pk_list).distinct().order_by(*orderings)
            if len(orderings):
                queryset = queryset.order_by(*orderings)

        return queryset