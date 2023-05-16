import logging

from rest_framework.permissions import BasePermission

from leaseslicensing.helpers import is_customer, is_internal

logger = logging.getLogger(__name__)


class IsInternalAPIView(BasePermission):
    def has_permission(self, request, view):
        if is_internal(request):
            if "DELETE" == request.method:
                return False

            return True
        if is_customer(request):
            return True
        return False


class IsInternalOrHasObjectDocumentsPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_internal(request):
            return True
        if is_customer(request):
            if not hasattr(obj, "can_user_view_documents"):
                raise AttributeError(
                    f"Object: {obj} must define a can_user_view_documents method to use this permission."
                )
            return obj.can_user_view_documents(request.user.id)

        return False
