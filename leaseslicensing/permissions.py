import logging

from rest_framework.permissions import BasePermission

from leaseslicensing.helpers import is_internal

logger = logging.getLogger(__name__)


class IsInternalAPIView(BasePermission):
    def has_permission(self, request, view):
        if is_internal(request):
            if "DELETE" == request.method:
                return False

            return True
        return False
