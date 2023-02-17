from django.db.models import Case, When, Q
from django.core.cache import cache
from django.conf import settings

from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework import serializers

from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from leaseslicensing.components.main.decorators import basic_exception_handler
import logging
import functools
import itertools

logger = logging.getLogger(__name__)

class LedgerDatatablesFilterBackend(DatatablesFilterBackend):
    """
    Class extending `DatatablesFilterBackend` to allow search in and ordering of querysets 
    with Ledger not-constrained foreign keys. Connects a model's ledger foreign key integer
    value to primary keys in ledger and maps search results and ordering back to the model.
    """

    LEDGER_LOOKUP_FIELDS = []

    def __init__(self, **kwargs):
        """Constructor

            Args:
                model (models.Model, optional): 
                    The table's model class
                ledger_lookup_fields (list, optional): 
                    The fields in the model that functions as the foreign key to ledger

            Usage:
                class MyModelFilterBackend(LedgerDatatablesFilterBackend):
                    def filter_queryset(self, request, queryset, view):
                        # Some code here ...
                        
                        # Apply searching and ordering here
                        queryset = self.apply_request(request, queryset, view,
                                    model=MyModel,
                                    ledger_lookup_fields=["submitter"] # Foreign key to ledger
                                    )

                        # Some more code here ...
                        return queryset
        """

        self.model = kwargs.get("model", None)
        # Int foreign keys in the model that are PKs in segregated ledger
        # E.g. `ind_applicant` can also be `proposal.ind_applicant`
        self.LEDGER_LOOKUP_FIELDS = kwargs.get("ledger_lookup_fields", ["ind_applicant",
                                                                        "submitter",
                                                                        "assigned_officer",
                                                                        "assigned_approver",
                                                                        "assigned_officer_id"])
        self.CACHE_PREFIX = "ledger_api_acounts_filtered_emailuser_"
        # Minimum amount of characters required to initiate searching the queryset
        self.SEARCH_THRESHOLD = 2


    @basic_exception_handler
    def split_list_to_dict(self, list_to_split, ledger_keys=[]):
        result_dict = {}

        # The ledger key for this list of dot-notation fields
        applicable_ledger_keys = [k for k in ledger_keys
                                  if any([k in l for l in list_to_split])]
        if len(applicable_ledger_keys) == 0:
            return result_dict

        for item in list_to_split:
            if '.' not in item:
                continue

            ledger_key_idx = 1
            item_split = item.split('.')
            for lkey in applicable_ledger_keys:
                if lkey in item_split:
                    ledger_key_idx = item.replace("-","").split(".").index(lkey) + 1

            key = ".".join(item_split[:ledger_key_idx])
            value = ".".join(item_split[ledger_key_idx:])
            result_dict.setdefault(key, []).append(value)
        return result_dict


    @basic_exception_handler
    def rgetattr(self, obj, attr, *args):
        def _getattr(obj, attr):
            if isinstance(obj, dict):
                return obj.get(attr, None)
            else:
                return getattr(obj, attr, *args) if hasattr(obj, attr) else None
        return functools.reduce(_getattr, [obj] + attr.split('.'))


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
    def ledger_cache(self, queryset, ledger_keys=[]):
        """
        Retrieves ledger accounts emailuser from cache. Creates a new cache if
        no cache exists

        Args:
            queryset (QuerySet):
                The database model's queryset
            ledger_keys (list<integer>, keyword argument):
                A list of fields in the model that function as foreign keys to ledger

        Returns:
            A ledger emailuser accounts queryset from cache
        """

        name = "leases"
        cache_key = f"{self.CACHE_PREFIX}{name}"
        
        # Query the ledger cache
        _ledger_cache = cache.get(cache_key)

        if _ledger_cache is None:
            logger.info(f"Setting new ledger user account cache for `{name}`")
            # Query ledger
            _ledger_cache = EmailUser.objects.all()
            # Cache
            cache.set(
                cache_key,
                _ledger_cache,
                settings.LOV_CACHE_TIMEOUT,
            )
        else:
            logger.info(f"Returning ledger user accounts for `{name}` from cache")

        # All ledger foreign keys for this model
        lfks = queryset.values_list(*ledger_keys)
        lfks = list(set(itertools.chain(*lfks)))
        # Filter by this model's ledger foreign keys
        ledger = _ledger_cache.filter(pk__in=lfks)

        return ledger


    @basic_exception_handler
    def apply_request(self, request, queryset, view, **kwargs):
        """
        Applies a query request to a queryset, searching for the request's
        `search_value` (if applicable) and ordering it.

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

        Returns:
            A searched in and ordered queryset
        """

        model = kwargs.get("model", self.model)
        if model is None:
            return serializers.ValidationError("No model provided or provided model is None.")
        
        ledger_lookup_fields = kwargs.get("ledger_lookup_fields", self.LEDGER_LOOKUP_FIELDS)

        query_model_list = []
        datatables_query = self.parse_datatables_query(request, view)
        search_value = ""
        if "search_value" in datatables_query and datatables_query["search_value"] is not None:
            search_value = datatables_query["search_value"].lower().strip()

        datatables_search_query = [q for q in datatables_query["fields"] if q["searchable"]==True]
        # Fields to search / order for
        datatables_search_attributes = [a for s in datatables_search_query for a in s["name"]]

        # Require at least two characters before searching
        if len(search_value) >= self.SEARCH_THRESHOLD:
            # queryset_cp = queryset.all() # A queryset copy

            # A dictionary of ledger foreign keys and search values
            ledger_attrs = {}
            # A list of search values that directly can be searched for in the model
            model_attrs = []
            # The resulting (searched for and ordered) queryset as a list
            query_model_list = []

            for attribute in datatables_search_attributes:
                _attr_parts = attribute.split("__")
                # Handle the top-level attribute being a "foreign key" to ledger
                # TODO put code in ledger back reference function
                if any( [attr in ledger_lookup_fields for attr in _attr_parts] ):
                    # The model attributes that are integer "foreign keys" to ledger
                    _fk_attrs = [attr for attr in _attr_parts if attr in ledger_lookup_fields]
                    # Add ledger attribute fields to a dict, as searching for them is more
                    # complicated (segregated database)
                    for attr in _fk_attrs:
                        if attr not in ledger_attrs:
                            # Create ledger attribute if not exists
                            ledger_attrs[attr] = {}

                        # Find the position of the ledger fk attribute,
                        # to handle e.g. `proposal__ind_applicant__name`
                        attr_idx = _attr_parts.index(attr) + 1
                        # Populate the dictionary of attributes in segregated architecture
                        _model_part, _ledger_part = "__".join(_attr_parts[:attr_idx]), ".".join(_attr_parts[attr_idx:])
                        if not _model_part in ledger_attrs[attr]:
                            ledger_attrs[attr][_model_part] = []
                        ledger_attrs[attr][_model_part].append(_ledger_part)

                else:
                    # Retrieve the attribute value from this model
                    model_attrs += [attribute]

            # Filter for model database fields first
            model_filter_dict = {f"{attr}__icontains": search_value for attr in model_attrs}
            model_qs_filtered = queryset.filter(Q(**model_filter_dict, _connector=Q.OR))
            # Add filtered model results to list
            query_model_list += [m for m in list(model_qs_filtered) if m not in query_model_list]

            # Ledger lookup fields for this model in double underscore-notation
            _ledger_fields_undscr = list(itertools.chain(*[list(ledger_attrs[k].keys())
                                                            for k in ledger_attrs.keys()]))
            # Get the cached ledger user
            ledger_cache = None
            if len(_ledger_fields_undscr) > 0:
                ledger_cache = self.ledger_cache(queryset, _ledger_fields_undscr)

            for attribute in ledger_attrs:
                # Ledger foreign keys
                _fks = list(set([self.rgetattr(m, k.replace("__", "."))
                                    for m in list(queryset)
                                    for k in _ledger_fields_undscr]))
                
                # A dictionary of search fields and values
                ledger_filter_dict = {f"{val}__icontains": search_value for key in ledger_attrs[attribute]
                                        for val in ledger_attrs[attribute][key]}

                # Filter the ledger cache
                ledger_qs_filtered = ledger_cache.filter(
                    Q(pk__in=_fks)).filter(
                    Q(**ledger_filter_dict, _connector=Q.OR))
                if ledger_qs_filtered.count() > 0:
                    logger.info(f"Found `{search_value}` in LEDGER attribute {_ledger_fields_undscr}: {_fks}")

                # List of ledger pk dicts, e.g. `[{'pk': 2}, {'pk': 1}]`, and filter model
                _pks = list(ledger_qs_filtered.values("pk"))
                # Map ledger pks back to model attribute, e.g. `{'submitter__in': [2]}`
                model_filter_dict = { f"{key}__in": [d["pk"] for d in _pks]
                                        for key in ledger_attrs[attribute] }
                model_qs_filtered = queryset.filter(Q(**model_filter_dict))
                # Append to the resulting queryset list
                query_model_list += [m for m in list(model_qs_filtered)
                                     if m not in query_model_list]

        else:
            # Cast queryset to list
            query_model_list = list(queryset)

        # Ordering
        fields = self.get_fields(request)
        orderings = self.get_ordering(request, view, fields)
        orderings_dotnot = [f.replace("__", ".")
                            for f in orderings[0].split(",")] if len(orderings) > 0 else []
        # Order fields that are not part of this model
        if any([sublist.replace("-", "") in ledger_lookup_fields
                for inner in orderings_dotnot
                for sublist in inner.split(".")]):
            ordering = ",".join(orderings_dotnot)
            # Ascending or descending
            reverse = ordering.startswith("-")
            # Handle ordering by ledger field
            if any([lf in ordering for lf in ledger_lookup_fields]):
                # Transform a list of dot-notation strings (key.field) to a dictionary in the form of {key:[fields]}
                ord_dict = self.split_list_to_dict(orderings_dotnot, ledger_keys=ledger_lookup_fields)
                # Get ledger accounts from cache
                _ledger_keys = [f.replace("-", "").replace(".", "__") for f in list(ord_dict.keys())]
                ledger_cache = self.ledger_cache(queryset, ledger_keys=_ledger_keys)
                # Order queryset list according to foreign key lookups in ledger entries
                model_fpks_sort = self.order_ledger_fks(ledger_cache, query_model_list, ord_dict)

                # Get a list of pkeys
                pk_list = [l.pk for l in query_model_list]
                # Preserve the order of the pkey list
                fpk_attr = list(ord_dict.keys())[0].replace("-", "").replace(".", "__")
                preserved_order = Case(*[When(**{fpk_attr:fpk, "then":pos}) for pos, fpk in enumerate(model_fpks_sort)])
            else:
                # Order list of models
                query_model_list = sorted(query_model_list, key=lambda p: self.rgetattr(
                    p, ordering.replace("-", "")), reverse=reverse)
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
    def order_ledger_fks(self, ledger, query_model_list, ord_dict):
        """
        Orders a list of querysets for a model according to ordering values in ledger,
        connecting integer "foreign keys" in the model to primary keys in the 
        segregated ledger database.

        Args:
            ledger (QuerySet):
                A ledger queryset
            query_model_list (list):
                This model as a list
            ord_dict (dictionary):
                A dictionary in the form of `{ledger_fk_in_model: [search_fields_in_ledger]}`

        Returns:
            A list of ledger foreign keys in the model ordered by ordering values in ledger
        """

        reverse = list(ord_dict.keys())[0].startswith("-")
        # Ledger "foreign keys" in model
        model_fpks = [self.rgetattr(model, attr.replace("-", ""))
                      for model in query_model_list
                      for attr in list(ord_dict.keys())]
        # Get a distinct list of ledger keys on which to order
        ledger_pks = list(set(model_fpks))
        # Get a list of ledger fields to order for
        ledger_orderings = [inner for outer in list(ord_dict.values()) for inner in outer]
        # Filter and sort ledger
        # ledger = EmailUser.objects.filter(pk__in=ledger_pks).order_by(*ledger_orderings)
        ledger = ledger.filter(pk__in=ledger_pks).order_by(*[f"-{l}"
                                                             if reverse else l for l in ledger_orderings])
        # List of ordered keys in ledger
        ledger_pk_list = [l.pk for l in list(ledger)]
        # Dictionary of counted ledger "foreign keys" in model
        model_fpks_cnt = {pk:model_fpks.count(pk) for pk in ledger_pks}
        # An expanded list of ledger "foreign keys"
        model_fpks_sort = [inner for outer in [[p]*model_fpks_cnt[p]
                                               for p in ledger_pk_list]
                                               for inner in outer]
        # Handle None-type ledger "foreign key", prepend or append the respective amount of None
        if reverse:
            model_fpks_sort = [None]*model_fpks_cnt.get(None, 0) + model_fpks_sort
        else:
            model_fpks_sort = model_fpks_sort + [None]*model_fpks_cnt.get(None, 0)

        # `model_fpks` grows with the amount of Ledger foreign keys, so have to divide here
        # to correctly compare with the size of the view's queryset
        if not len(model_fpks_sort)/len(ord_dict.keys()) == len(query_model_list):
            # TODO Try to delete cache
            raise serializers.ValidationError("`model_attr_sort` does not match length of QuerySet")

        return model_fpks_sort
