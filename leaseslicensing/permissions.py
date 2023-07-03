import logging

from rest_framework.permissions import BasePermission

from leaseslicensing.helpers import (
    is_approver,
    is_assessor,
    is_compliance_referee,
    is_customer,
    is_internal,
    is_referee,
)

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


class IsAsignedAssessor(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if not is_internal(request):
            return False

        return is_assessor(request)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        return request.user.id == obj.assigned_to


class IsAssignedReferee(BasePermission):
    def has_permission(self, request, view):
        logger.debug(f"IsAssignedReferee: {request.user.id}")
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if not is_internal(request):
            return False

        return is_referee(request)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        logger.debug(f"Referee: {request.user.id} Referral: {obj.referral}")
        return request.user.id == obj.referral


class IsAssignedComplianceReferee(BasePermission):
    def has_permission(self, request, view):
        logger.debug(f"IsAssignedReferee: {request.user.id}")
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if not is_internal(request):
            return False

        return is_compliance_referee(request)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        logger.debug(f"Referee: {request.user.id} Referral: {obj.referral}")
        return request.user.id == obj.referral


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
