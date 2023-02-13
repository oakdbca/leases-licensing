from django.db.models import Case, When
from django.core.cache import cache
from django.conf import settings

from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework import serializers
from rest_framework.test import APIRequestFactory as RequestFactory
from rest_framework.request import Request

from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from leaseslicensing.components.main.decorators import basic_exception_handler
import logging
import functools
import itertools

logger = logging.getLogger(__name__)

class LedgerDatatablesFilterBackend(DatatablesFilterBackend):
    """
    Class extending `DatatablesFilterBackend` to allow search in and ordering of querysets 
    with Ledger not-constrained foreign keys
    """

    LEDGER_LOOKUP_FIELDS = []
    SPECIAL_ORDERING_FIELDS = []


    def __init__(self, **kwargs):
        """Constructor

            Args:
                model (models.Model, optional): 
                    The table's model class
                ledger_lookup_fields (list, optional): 
                    The field in the model that functions as the foreign key to ledger
                special_ordering_fields (list, optional): 
                    Fields that are not part of the model and need special ordering treatment

            Usage:
                class MyFilterBackend(LedgerDatatablesFilterBackend):
                    def filter_queryset(self, request, queryset, view):
                        # Some code here ...
                        
                        queryset = self.apply_request(request, queryset, view,
                                    model=Compliance,
                                    ledger_lookup_fields=["submitter"], # Foreign key to ledger
                                    special_ordering_fields=["application_type", "holder", "submitter"])

                        # Some more code here ...
                        return queryset
        """

        self.model = kwargs.get("model", None)
        self.LEDGER_LOOKUP_FIELDS = kwargs.get("ledger_lookup_fields", ["submitter"])
        self.SPECIAL_ORDERING_FIELDS = kwargs.get("special_ordering_fields", ["submitter"])
        self.CACHE_PREFIX = "ledger_api_acounts_filtered_emailuser_"


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
    def search_attrs(self, queryset, search_value, attributes, model, ledger_lookup_fields):
        # ledger foreign key attributes in leases (e.g. submitter)
        _ledger_attrs = {}
        # First search leases attributes and store ledger foreign keys for later
        for attribute in attributes:
            _attr_parts = attribute.split(".")
            # Handle the top-level attribute being a "foreign key" to ledger
            if _attr_parts[0] in ledger_lookup_fields:
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
                
                # Get the cached ledger user
                ledger_cache = self.ledger_cache(queryset, model, ledger_lookup_fields)
                # Check that only one entry is returned
                # ledger = EmailUser.objects.filter(pk=_fk).values(*_ledger_attrs[attribute])
                ledger = ledger_cache.filter(pk=_fk).values(*_ledger_attrs[attribute])
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
    def ledger_cache(self, queryset, model, ledger_lookup_fields):
        """
        Retrieves ledger accounts emailuser from cache. Creates a new cache if for this model
        no cache exists

        Args:
            queryset (QuerySet):
                The database model's queryset
            model (models.Model, keyword argument): 
                The table's model class
            ledger_lookup_fields (list, keyword argument): 
                The field in the model that functions as the foreign key to ledger

        Returns:
            A ledger emailuser accounts queryset from cashe
        """

        name = model.__name__ if hasattr(model, "__name__") \
            else model.__class__.__name__ if hasattr(model, "__class__") \
            else "default"
        
        # Query the ledger cache
        ledger_cache = cache.get(f"{self.CACHE_PREFIX}{name}")
        if ledger_cache is None:
            logger.info(f"Setting new ledger user account cache for model `{name}`")
            settings.LOV_CACHE_TIMEOUT
            # All ledger foreign keys for this model
            lfks = queryset.values_list(*ledger_lookup_fields)
            lfks = list(set(itertools.chain(*lfks)))
            # Query ledger
            ledger_cache = EmailUser.objects.filter(pk__in=lfks)
            cache.set(
                f"{self.CACHE_PREFIX}{name}",
                ledger_cache,
                settings.LOV_CACHE_TIMEOUT,
            )
        else:
            logger.info(f"Returning ledger user accounts for model `{name}` from cache")

        return ledger_cache


    @basic_exception_handler
    def apply_request(self, request, queryset, view, **kwargs):
        """
        Applies a query request to a queryset, searching for the requests `search_value` (if applicable)
        and ordering it.

        Args:
            request (Request):
                The Rest API request
            queryset (QuerySet):
                The database model's queryset
            view (ModelViewSet):
                The view to query for
            model (models.Model, keyword argument): 
                The table's model class
            ledger_lookup_fields (list, keyword argument): 
                The field in the model that functions as the foreign key to ledger
            special_ordering_fields (list, keyword argument): 
                Fields that are not part of the model and need special ordering treatment

        Returns:
            A searched in and ordered queryset
        """

        model = kwargs.get("model", self.model)
        if model is None:
            return serializers.ValidationError("No model provided or provided model is None.")
        
        ledger_lookup_fields = kwargs.get("ledger_lookup_fields", self.LEDGER_LOOKUP_FIELDS)
        special_ordering_fields = kwargs.get("special_ordering_fields", self.SPECIAL_ORDERING_FIELDS)

        query_model_list = []
        datatables_query = self.parse_datatables_query(request, view)
        search_value = ""
        if "search_value" in datatables_query and datatables_query["search_value"] is not None:
            search_value = datatables_query["search_value"].lower().strip()

        # Fields to search / order for
        datatables_search_query = [q for q in datatables_query["fields"] if q["searchable"]==True]
        datatables_search_attributes = [a.replace('__', '.') for s in datatables_search_query for a in s["name"]]
        # Require at least two characters before searching
        if len(search_value) > 1:
            queryset_len = queryset.count()
            queryset_cp = queryset.all() # A queryset copy
            # Try to search by filtering the queryset first for any field
            # that is not in `special_ordering_fields`
            if queryset_len > 0:
                queryset_cp = self._original_filter_queryset_special(
                    request, queryset, view, special_ordering_fields)
                
            # If the previous search returns nothing directly search the queryset
            if queryset_cp.count() > 0:
                query_model_list = list(queryset_cp)
            else:
                # TODO only search the fields that are not part of the model, i.e. `special_ordering_fields`
                query_model_list = list(filter(lambda model: self.search_attrs(
                    queryset, search_value, datatables_search_attributes, model, ledger_lookup_fields), 
                    list(queryset)))
        else:
            # Cast queryset to list
            query_model_list = list(queryset)

        # Ordering
        fields = self.get_fields(request)
        orderings = self.get_ordering(request, view, fields)
        orderings_dotnot = [f.replace("__", ".") for f in orderings[0].split(",")] if len(orderings) > 0 else []
        # Order fields that are not part of this model
        if any([sublist.replace("-", "") in special_ordering_fields for inner in orderings_dotnot for sublist in inner.split(".")]):
            ordering = ",".join(orderings_dotnot)
            # Ascending or descending
            reverse = ordering.startswith("-")
            # Handle ordering by ledger field
            if ordering.replace("-", "").split(".")[0] in ledger_lookup_fields:
                # Transform a list dot-notation strings (key.field) to a dictionary in the form of {key:[fields]}
                ord_dict = self.split_list_to_dict(orderings_dotnot)
                # Ledger "foreign keys" in model
                model_fpks = [getattr(model, attr.replace("-", "")) for model in query_model_list for attr in list(ord_dict.keys())]
                # Get a distinct list of ledger keys on which to order
                ledger_pks = list(set(model_fpks))
                # Get a list of ledger fields to order for
                ledger_orderings = [inner for outer in list(ord_dict.values()) for inner in outer]
                
                # Get ledger accounts from cache
                ledger_cache = self.ledger_cache(queryset, model, ledger_lookup_fields)
                # ledger = EmailUser.objects.filter(pk__in=ledger_pks).order_by(*ledger_orderings)
                ledger = ledger_cache.filter(pk__in=ledger_pks).order_by(*ledger_orderings)

                # List of ordered keys in ledger
                ledger_pk_list = [l.pk for l in list(ledger)]
                # Dictionary of counted ledger "foreign keys" in model
                model_fpks_cnt = {pk:model_fpks.count(pk) for pk in ledger_pks}
                # An expanded list of ledger "foreign keys"
                model_fpks_sort = [inner for outer in [[p]*model_fpks_cnt[p] for p in ledger_pk_list] for inner in outer]
                # Handle None-type ledger "foreign key", prepend or append the respective amount of None
                if reverse:
                    model_fpks_sort = [None]*model_fpks_cnt.get(None, 0) + model_fpks_sort
                else:
                    model_fpks_sort = model_fpks_sort + [None]*model_fpks_cnt.get(None, 0)

                # `model_fpks` grows with the amount of Ledger foreign keys, so have to divide here 
                # to correctly compare with the size of the view's queryset
                # TODO is this correct?
                if len(model_fpks_sort)/len(ord_dict.keys()) != len(query_model_list):
                    raise serializers.ValidationError("`model_attr_sort` does not match length of QuerySet")
                # check search in assigned officer
                # Get a list of keys
                pk_list = [l.pk for l in query_model_list]
                # Preserve the order of the list of keys
                fpk_attr = list(ord_dict.keys())[0].replace("-", "")
                preserved_order = Case(*[When(**{fpk_attr:fpk, "then":pos}) for pos, fpk in enumerate(model_fpks_sort)])
            else:
                # Order list of models
                query_model_list = sorted(query_model_list, key=lambda p: self.rgetattr(p, ordering.replace("-", "")), reverse=reverse)
                # Get a list of keys
                pk_list = [l.pk for l in query_model_list]
                # Preserve the order of the list of keys
                preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])

            # Convert back to Model Queryset using the sorting of `query_model_list`
            queryset = model.objects.filter(pk__in=pk_list).distinct().order_by(preserved_order)
        else:
            # Convert back to Model Queryset
            pk_list = [l.pk for l in query_model_list]
            queryset = model.objects.filter(pk__in=pk_list).distinct().order_by(*orderings)
            if len(orderings):
                queryset = queryset.order_by(*orderings)

        return queryset
    

    @basic_exception_handler
    def _original_filter_queryset_special(self, request, queryset, view, special_ordering_fields):
        """
        Filters a queryset with a request omitting fields from `special_ordering_fields`
        """

        request_path = request.path # the relative API url
        request_ = request.GET.copy()
        # Replace request fields that would otherwise throw an error (because they are not part of the model)
        # with an empty string
        for k, v in dict(request_).items():
            if any([v[0].startswith(f) for f in special_ordering_fields]):
                request_[k] = ''

        # Create a new Request object from the modified request
        factory = RequestFactory()
        request_cp = Request(factory.get(request_path, request_, format="json"))
        request_cp.accepted_renderer = request.accepted_renderer

        # Filter the queryset with the modified request
        queryset_cp = super(LedgerDatatablesFilterBackend, self).filter_queryset(
            request_cp, queryset, view
        )

        return queryset_cp