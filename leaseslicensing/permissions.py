import logging

from rest_framework.permissions import BasePermission

from leaseslicensing.components.organisations.utils import can_admin_org
from leaseslicensing.helpers import is_customer, is_internal

logger = logging.getLogger(__name__)


class IsInternalAPIViewPermission(BasePermission):
    def has_permission(self, request, view):
        if is_internal(request):
            if "DELETE" == request.method:
                return False

            return True
        if is_customer(request):
            return True
        return False


class IsInternalOrHasObjectPermissionAPIViewPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_internal(request):
            return True
        if is_customer(request):
            if obj.ind_applicant:
                return request.user.id in [
                    obj.applicant,
                    obj.submitter,
                    obj.proxy_applicant,
                ]
            if obj.org_applicant:
                return can_admin_org(obj.org_applicant, request.user.id)
        return False
