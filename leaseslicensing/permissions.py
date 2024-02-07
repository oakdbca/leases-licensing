import logging

from rest_framework.permissions import BasePermission

from leaseslicensing.helpers import (
    is_approver,
    is_assessor,
    is_competitive_process_editor,
    is_compliance_referee,
    is_customer,
    is_finance_officer,
    is_internal,
    is_referee,
)

logger = logging.getLogger(__name__)


class IsInternal(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if is_internal(request):
            if "DELETE" == request.method:
                return False

            return True
        return False


class IsFinanceOfficer(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if is_finance_officer(request):
            return True
        return False


class HasObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if is_customer(request):
            if not hasattr(obj, "user_has_object_permission"):
                raise AttributeError(
                    f"Object: {obj} must define a user_has_object_permission method to use this permission."
                )
            return obj.user_has_object_permission(request.user.id)

        return False


class IsInternalOrHasObjectPermission(BasePermission):
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

        return request.user.id == obj.referral


class IsComplianceReferee(BasePermission):
    def has_permission(self, request, view):
        return is_compliance_referee(request)


class IsAssignedComplianceReferee(BasePermission):
    def has_permission(self, request, view):
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


class IsAssessor(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return is_assessor(request)


class IsApprover(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return is_approver(request)


class IsCompetitiveProcessEditor(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return is_competitive_process_editor(request)
