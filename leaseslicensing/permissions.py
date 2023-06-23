import logging

from rest_framework.permissions import BasePermission

from leaseslicensing.helpers import is_customer, is_internal, is_assessor, is_approver

logger = logging.getLogger(__name__)


class IsInternalAPIView(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if is_internal(request):
            if "DELETE" == request.method:
                return False

            return True
        return False


class IsInternalOrHasObjectDocumentsPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if is_internal(request):
            return True
        if is_customer(request):
            if not hasattr(obj, "user_has_object_permission"):
                raise AttributeError(
                    f"Object: {obj} must define a user_has_object_permission method to use this permission."
                )
            return obj.user_has_object_permission(request.user.id)

        return False


class IsAssessorOrReferrer(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if request.user.is_superuser:
            return True

        if not is_internal(request):
            return False

        return is_assessor(request) or is_approver(request)
