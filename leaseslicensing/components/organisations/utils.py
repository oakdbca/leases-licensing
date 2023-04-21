import random
import string


def can_manage_org(organisation, user):
    from leaseslicensing.components.organisations.models import (
        OrganisationAccessGroup,
        UserDelegation,
    )

    if user.is_anonymous:
        return False
    if user.is_superuser:
        return True

    try:
        # Not 100% sure what was intended here see git history for what was here before
        user_delegation = UserDelegation.objects.get(
            organisation=organisation, user=user.id
        )
        return can_admin_org(organisation, user)
    except UserDelegation.DoesNotExist:
        try:
            group = OrganisationAccessGroup.objects.first()
            if group:
                group.members.get(id=user.id)
            return True
        except OrganisationAccessGroup.DoesNotExist:
            return False


def is_last_admin(organisation, user):
    from leaseslicensing.components.organisations.models import OrganisationContact

    """ A check for whether the user contact is the only administrator for the Organisation. """
    _last_admin = False
    try:
        _admin_contacts = OrganisationContact.objects.filter(
            organisation_id=organisation,
            user_status="active",
            user_role="organisation_admin",
        )
        _is_admin = _admin_contacts.filter(email=user.email).exists()
        if _is_admin and _admin_contacts.count() < 2:
            _last_admin = True
    except OrganisationContact.DoesNotExist:
        _last_admin = False
    return _last_admin


def can_admin_org(organisation, user):
    from leaseslicensing.components.organisations.models import OrganisationContact

    try:
        org_contact = OrganisationContact.objects.get(
            organisation_id=organisation, email=user.email
        )
        return org_contact.can_edit
    except OrganisationContact.DoesNotExist:
        return False


def can_relink(organisation, user):
    from leaseslicensing.components.organisations.models import OrganisationContact

    """ Check user contact can be relinked to the Organisation. """
    _can_relink = False
    try:
        _can_relink = OrganisationContact.objects.filter(
            organisation_id=organisation.id, email=user.email, user_status="unlinked"
        ).exists()
    except OrganisationContact.DoesNotExist:
        _can_relink = False
    return _can_relink


def can_approve(organisation, user):
    from leaseslicensing.components.organisations.models import OrganisationContact

    """ Check user contact linkage to the Organisation can be approved. """
    _can_approve = False
    try:
        _can_approve = OrganisationContact.objects.filter(
            organisation_id=organisation.id,
            email=user.email,
            user_status__in=("declined", "pending"),
        ).exists()
    except OrganisationContact.DoesNotExist:
        _can_approve = False
    return _can_approve


def is_consultant(organisation, user):
    from leaseslicensing.components.organisations.models import OrganisationContact

    try:
        org_contact = OrganisationContact.objects.get(
            organisation_id=organisation, email=user.email
        )
        return org_contact.check_consultant
    except OrganisationContact.DoesNotExist:
        return False


def random_generator(size=12, chars=string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def has_atleast_one_admin(organisation):
    from leaseslicensing.components.organisations.models import OrganisationContact

    """ A check for whether Organisation has atlease one admin user """
    _atleast_one_admin = False
    try:
        _admin_contacts = OrganisationContact.objects.filter(
            organisation_id=organisation,
            user_status="active",
            user_role="organisation_admin",
            is_admin=True,
        )
        if _admin_contacts.count() > 0:
            _atleast_one_admin = True
    except OrganisationContact.DoesNotExist:
        _atleast_one_admin = False
    return _atleast_one_admin


def get_organisation_ids_for_user(email_user_id):
    # Todo: If we are using the UserDelegates model, then use this instead otherwise remove this code:
    # from leaseslicensing.components.organisations.models import UserDelegation
    # return UserDelegation.objects.filter(user=email_user_id).values_list("organisation__id", flat=True)
    from leaseslicensing.components.organisations.models import Organisation

    return list(
        Organisation.objects.filter(delegates__contains=[email_user_id]).values_list(
            "id", flat=True
        )
    )
