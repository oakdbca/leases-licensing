import logging

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.text import slugify
from ledger_api_client.managed_models import SystemGroupPermission
from ledger_api_client.utils import (
    create_organisation,
    get_organisation,
    get_search_organisation,
)
from rest_framework import status

from leaseslicensing.components.main.models import (
    CommunicationsLogEntry,
    Document,
    SecureFileField,
    UserAction,
)
from leaseslicensing.components.organisations.emails import (  # send_organisation_request_accept_email_notification,
    send_org_access_group_request_accept_email_notification,
    send_organisation_contact_adminuser_email_notification,
    send_organisation_contact_decline_email_notification,
    send_organisation_contact_suspend_email_notification,
    send_organisation_contact_user_email_notification,
    send_organisation_link_email_notification,
    send_organisation_reinstate_email_notification,
    send_organisation_request_accept_email_notification,
    send_organisation_request_decline_email_notification,
    send_organisation_request_email_notification,
    send_organisation_request_link_email_notification,
    send_organisation_unlink_email_notification,
)
from leaseslicensing.components.organisations.exceptions import (
    UnableToRetrieveLedgerOrganisation,
)
from leaseslicensing.components.organisations.utils import random_generator
from leaseslicensing.helpers import belongs_to_by_user_id
from leaseslicensing.ledger_api_utils import retrieve_email_user

# @python_2_unicode_compatible

logger = logging.getLogger(__name__)


class Organisation(models.Model):
    ledger_organisation_id = models.IntegerField(
        unique=True, verbose_name="Ledger Organisation ID"
    )  # Ledger Organisation
    ledger_organisation_name = models.CharField(
        max_length=255,
        verbose_name="Ledger Organisation Name",
        editable=False,
        default="",
    )
    ledger_organisation_trading_name = models.CharField(
        max_length=255,
        verbose_name="Ledger Organisation Trading Name",
        editable=False,
        default="",
    )
    ledger_organisation_abn = models.CharField(
        max_length=50,
        verbose_name="Ledger Organisation ABN",
        editable=False,
        default="",
    )
    ledger_organisation_email = models.EmailField(
        verbose_name="Ledger Organisation Email",
        null=True,
        blank=True,
        editable=False,
    )
    admin_pin_one = models.CharField(max_length=50, blank=True)
    admin_pin_two = models.CharField(max_length=50, blank=True)
    user_pin_one = models.CharField(max_length=50, blank=True)
    user_pin_two = models.CharField(max_length=50, blank=True)

    class Meta:
        app_label = "leaseslicensing"

    def __str__(self):
        if self.ledger_organisation_name and self.ledger_organisation_abn:
            return (
                f"{self.ledger_organisation_name} (ABN: {self.ledger_organisation_abn})"
            )
        if self.ledger_organisation_name:
            return self.ledger_organisation_name
        return f"Ledger Organisation ID: {self.ledger_organisation_id})"

    def save(self, *args, **kwargs):
        self.ledger_organisation_name = self.ledger_organisation["organisation_name"]
        self.ledger_organisation_abn = self.ledger_organisation["organisation_abn"]
        if self.ledger_organisation["organisation_trading_name"]:
            self.ledger_organisation_trading_name = self.ledger_organisation[
                "organisation_trading_name"
            ]

        if self.ledger_organisation["organisation_email"]:
            self.ledger_organisation_email = self.ledger_organisation[
                "organisation_email"
            ]
        super().save(*args, **kwargs)

    @property
    def ledger_organisation(self):
        if self.ledger_organisation_id:
            cache_key = settings.CACHE_KEY_LEDGER_ORGANISATION.format(
                self.ledger_organisation_id
            )
            organisation = cache.get(cache_key)
            if organisation is None:
                logger.info(
                    f"Retrieving organisation {self.ledger_organisation_id} from ledger."
                )
                organisation_response = get_organisation(self.ledger_organisation_id)
                if status.HTTP_200_OK == organisation_response["status"]:
                    organisation = organisation_response["data"]
                    cache.set(cache_key, organisation, settings.CACHE_TIMEOUT_24_HOURS)
                else:
                    error_message = (
                        "CRITICAL: Unable to retrieve organisation "
                        f"{self.ledger_organisation_id} from ledger."
                    )
                    logger.error(error_message)
                    raise UnableToRetrieveLedgerOrganisation(error_message)
                logger.info(f"Retrieved organisation {organisation} from ledger.")
            return organisation

        critical_message = (
            f"CRITICAL: Organisation: {self.id} has no ledger organisation attached."
        )
        logger.critical(critical_message)
        return None

    @property
    def delegate_email_users(self):
        return OrganisationContact.objects.filter(
            organisation=self, user__in=self.delegates
        )

    def log_user_action(self, action, request):
        return OrganisationAction.log_action(self, action, request.user)

    def validate_pins(self, pin1, pin2, request):
        try:
            val_admin = self.admin_pin_one == pin1 and self.admin_pin_two == pin2
            val_user = self.user_pin_one == pin1 and self.user_pin_two == pin2
            if val_admin:
                val = val_admin
                role = OrganisationContact.USER_ROLE_CHOICE_ADMIN
            elif val_user:
                val = val_user
                role = OrganisationContact.USER_ROLE_CHOICE_USER
            else:
                return False

            self.add_user_contact(request.user, request, role)
            return val
        except Exception:
            return None

    def check_user_contact(self, request, role):
        user = request.user
        try:
            org = OrganisationContact.objects.create(
                user=user.id,
                organisation=self,
                first_name=user.first_name,
                last_name=user.last_name,
                mobile_number=user.mobile_number,
                phone_number=user.phone_number,
                fax_number=user.fax_number,
                email=user.email,
                user_role=role,
                user_status=OrganisationContact.USER_STATUS_CHOICE_PENDING,
            )
            return org
        except Exception:
            return False

    @transaction.atomic
    def add_user_contact(self, user, request, role):
        contact, created = OrganisationContact.objects.get_or_create(
            user=user.id,
            organisation=self,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            defaults={
                "mobile_number": user.mobile_number,
                "phone_number": user.phone_number,
                "fax_number": user.fax_number,
                "user_role": role,
                "user_status": OrganisationContact.USER_STATUS_CHOICE_PENDING,
            },
        )

        if not created:
            contact.mobile_number = user.mobile_number
            contact.phone_number = user.phone_number
            contact.fax_number = user.fax_number
            contact.user_role = role
            contact.user_status = OrganisationContact.USER_STATUS_CHOICE_PENDING
            contact.save()

        # log linking
        self.log_user_action(
            OrganisationAction.ACTION_CONTACT_ADDED.format(
                f"{user.first_name} {user.last_name}({user.email})"
            ),
            request,
        )

    def update_organisation(self, request):
        # log organisation details updated
        # (eg ../internal/organisations/access/2) - incorrect - this is for OrganisationRequesti not Organisation
        # should be ../internal/organisations/1
        with transaction.atomic():
            self.log_user_action(OrganisationAction.ACTION_UPDATE_ORGANISATION, request)

    def update_address(self, request):
        self.log_user_action(OrganisationAction.ACTION_UPDATE_ADDRESS, request)

    def update_contacts(self, request):
        contact = self.contact.last()
        self.log_user_action(
            OrganisationAction.ACTION_UPDATE_CONTACTS.format(
                f"{contact.first_name} {contact.last_name}({contact.email})"
            ),
            request,
        )

    def generate_pins(self):
        self.admin_pin_one = self._generate_pin()
        self.admin_pin_two = self._generate_pin()
        self.user_pin_one = self._generate_pin()
        self.user_pin_two = self._generate_pin()
        self.save()

    def _generate_pin(self):
        return random_generator()

    def send_organisation_request_link_notification(self, request):
        # Notify each Admin member of request to be linked to org.
        contacts = OrganisationContact.objects.filter(
            organisation_id=self.id,
            user_role=OrganisationContact.USER_ROLE_CHOICE_ADMIN,
            user_status=OrganisationContact.USER_STATUS_CHOICE_ACTIVE,
        )
        recipients = [c.email for c in contacts]
        send_organisation_request_link_email_notification(self, request, recipients)

    @staticmethod
    def existence(abn):
        try:
            organisation = Organisation.objects.get(organisation_abn=abn)
            if organisation.admin_user_count:
                return {
                    "exists": True,
                    "id": organisation.id,
                    "first_five": organisation.first_five,
                }
            return {"exists": False}

        except Organisation.DoesNotExist:
            return {"exists": False}

    @transaction.atomic
    def accept_user(self, user, request):
        delegate, created = UserDelegation.objects.get_or_create(
            organisation=self, user=user.id
        )
        if created:
            logger.info(f"Created User Delegation: {delegate}")

        try:
            org_contact = OrganisationContact.objects.get(
                organisation=self, email=user.email
            )
            org_contact.user_status = OrganisationContact.USER_STATUS_CHOICE_ACTIVE
            org_contact.save()
        except OrganisationContact.DoesNotExist:
            raise ValidationError(
                f"Organisation Contact with for {self} with email {user.email} does not exist."
            )

        # log linking
        self.log_user_action(
            OrganisationAction.ACTION_LINK.format(
                "{} {}({})".format(
                    org_contact.first_name,
                    org_contact.last_name,
                    org_contact.email,
                )
            ),
            request,
        )
        send_organisation_link_email_notification(user, request.user, self, request)

    @transaction.atomic
    def decline_user(self, user, request):
        try:
            org_contact = OrganisationContact.objects.get(
                organisation=self, email=user.email
            )
            org_contact.user_status = OrganisationContact.USER_STATUS_CHOICE_DECLINED
            org_contact.save()
        except OrganisationContact.DoesNotExist:
            return

        OrganisationContactDeclinedDetails.objects.create(
            officer=request.user.id, request=org_contact
        )

        # log linking
        self.log_user_action(
            OrganisationAction.ACTION_CONTACT_DECLINED.format(
                f"{user.first_name} {user.last_name}({user.email})"
            ),
            request,
        )
        send_organisation_contact_decline_email_notification(
            user, request.user, self, request
        )

    @transaction.atomic
    def link_user(self, user, request):
        user_delegation, created = UserDelegation.objects.get_or_create(
            organisation=self, user=user.id
        )
        if created:
            logger.info(f"Created User Delegation: {user_delegation}")

        # Create contact person
        OrganisationContact.objects.get_or_create(
            user=user.id,
            organisation=self,
            first_name=user.first_name,
            last_name=user.last_name,
            mobile_number=user.mobile_number,
            phone_number=user.phone_number,
            fax_number=user.fax_number,
            email=user.email,
            user_role=OrganisationContact.USER_ROLE_CHOICE_ADMIN,
            user_status=OrganisationContact.USER_STATUS_CHOICE_PENDING,
        )

        # log linking
        self.log_user_action(
            OrganisationAction.ACTION_LINK.format(
                "{} {}({})".format(
                    user.first_name,
                    user.last_name,
                    user.email,
                )
            ),
            request,
        )

        # send email
        send_organisation_link_email_notification(user, request.user, self, request)

    @transaction.atomic
    def accept_declined_user(self, user, request):
        user_delegation, created = UserDelegation.objects.get_or_create(
            organisation=self, user=user.id
        )
        if created:
            logger.info(f"Created User Delegation: {user_delegation}")

        # Mark organisation contact as active
        try:
            org_contact = OrganisationContact.objects.get(
                organisation=self, email=user.email
            )
        except OrganisationContact.DoesNotExist:
            raise ValidationError(
                f"Organisation Contact with email {user.email} for {self} does not exist."
            )

        # We will make them a standard user by default.
        # An admin can promote their priveleges later if necessary.
        org_contact.user_role = OrganisationContact.USER_ROLE_CHOICE_USER
        org_contact.user_status = OrganisationContact.USER_STATUS_CHOICE_ACTIVE
        org_contact.save()

        # log linking
        self.log_user_action(
            OrganisationAction.ACTION_LINK.format(
                "{} {}({})".format(
                    user.first_name,
                    user.last_name,
                    user.email,
                )
            ),
            request,
        )

        # send email
        send_organisation_link_email_notification(user, request.user, self, request)

    @transaction.atomic
    def relink_user(self, user, request):
        user_delegation, created = UserDelegation.objects.get_or_create(
            organisation=self, user=user.id
        )
        if created:
            logger.info(f"Created User Delegation: {user_delegation}")

        # Mark organisation contact as active
        try:
            org_contact = OrganisationContact.objects.get(
                organisation=self, email=user.email
            )
            org_contact.user_status = OrganisationContact.USER_STATUS_CHOICE_ACTIVE
            org_contact.save()
        except OrganisationContact.DoesNotExist:
            pass

        # log linking
        self.log_user_action(
            OrganisationAction.ACTION_MAKE_CONTACT_REINSTATE.format(
                "{} {}({})".format(
                    user.first_name,
                    user.last_name,
                    user.email,
                )
            ),
            request,
        )

        # send email
        send_organisation_reinstate_email_notification(
            user, request.user, self, request
        )

    @transaction.atomic
    def unlink_user(self, user, request):
        try:
            delegate = UserDelegation.objects.get(organisation=self, user=user.id)
        except UserDelegation.DoesNotExist:
            raise ValidationError(f"This user is not a member of {self}")

        # Mark the organisation contact as unlinked
        try:
            org_contact = OrganisationContact.objects.get(
                organisation=self, email=user.email
            )
        except OrganisationContact.DoesNotExist:
            raise ValidationError(
                f"Organisation Contact with for {self} with email {user.email} does not exist."
            )

        if org_contact.user_role == OrganisationContact.USER_ROLE_CHOICE_ADMIN:
            if (
                OrganisationContact.objects.filter(
                    organisation=self,
                    user_role=OrganisationContact.USER_ROLE_CHOICE_ADMIN,
                    user_status=OrganisationContact.USER_STATUS_CHOICE_ACTIVE,
                ).count()
                == 1
            ):
                if user.id == request.user.id:
                    raise ValidationError(
                        "You are the last active organisation administrator. You cannot unlink yourself."
                    )
                else:
                    raise ValidationError(
                        "This user is the last active organisation administrator."
                    )

        org_contact.user_status = OrganisationContact.USER_STATUS_CHOICE_UNLINKED
        org_contact.save()

        # Mark the most recent organisation request for this organisation as unlinked
        organisation_request = OrganisationRequest.objects.filter(
            organisation=self, requester=user.id
        ).last()
        if organisation_request:
            organisation_request.status = OrganisationRequest.STATUS_CHOICE_UNLINKED
            organisation_request.save()

        # delete delegate
        delegate.delete()

        # log linking
        self.log_user_action(
            OrganisationAction.ACTION_UNLINK.format(
                "{} {}({})".format(
                    org_contact.first_name,
                    org_contact.last_name,
                    org_contact.email,
                )
            ),
            request,
        )
        # send email
        send_organisation_unlink_email_notification(user, request.user, self, request)

    @transaction.atomic
    def make_admin_user(self, user, request):
        try:
            UserDelegation.objects.get(organisation=self, user=user.id)
        except UserDelegation.DoesNotExist:
            raise ValidationError(
                f"User Delegation with user id {user.id} does not exist for organisation {self}"
            )

        # Mark user as admin
        try:
            org_contact = OrganisationContact.objects.get(
                organisation=self, email=user.email
            )
            org_contact.user_role = OrganisationContact.USER_ROLE_CHOICE_ADMIN
            org_contact.save()
        except OrganisationContact.DoesNotExist:
            pass

        # log linking
        self.log_user_action(
            OrganisationAction.ACTION_MAKE_CONTACT_ADMIN.format(
                "{} {}({})".format(
                    user.first_name,
                    user.last_name,
                    user.email,
                )
            ),
            request,
        )
        # send email
        send_organisation_contact_adminuser_email_notification(
            user, request.user, self, request
        )

    @transaction.atomic
    def make_user(self, user, request):
        try:
            UserDelegation.objects.get(organisation=self, user=user.id)
        except UserDelegation.DoesNotExist:
            raise ValidationError(
                f"User Delegation with user id {user.id} does not exist for organisation {self}"
            )
        try:
            org_contact = OrganisationContact.objects.get(
                organisation=self, email=user.email
            )
        except OrganisationContact.DoesNotExist:
            raise ValidationError(
                f"Organisation Contact with email {user.email} for {self} does not exist."
            )

        # Demote the user to an organisation user
        if (
            org_contact.user_role == OrganisationContact.USER_ROLE_CHOICE_ADMIN
            and self.admin_user_count == 1
        ):
            # Last admin user should not be able to make himself user.
            raise ValidationError(
                "This user is the last active organisation administrator so they can't be demoted."
            )
        else:
            org_contact.user_role = OrganisationContact.USER_ROLE_CHOICE_USER
            org_contact.save()

        # log linking
        self.log_user_action(
            OrganisationAction.ACTION_MAKE_CONTACT_USER.format(
                "{} {}({})".format(
                    user.first_name,
                    user.last_name,
                    user.email,
                )
            ),
            request,
        )
        # send email
        send_organisation_contact_user_email_notification(
            user, request.user, self, request
        )

    @transaction.atomic
    def suspend_user(self, user, request):
        try:
            UserDelegation.objects.get(organisation=self, user=user.id)
        except UserDelegation.DoesNotExist:
            raise ValidationError(
                f"User Delegation with user id {user.id} does not exist for organisation {self}"
            )

        # Mark organisation contact as suspended
        try:
            org_contact = OrganisationContact.objects.get(
                organisation=self, email=user.email
            )
        except OrganisationContact.DoesNotExist:
            raise ValidationError(
                f"Organisation Contact with email {user.email} for {self} does not exist."
            )

        org_contact.user_status = OrganisationContact.USER_STATUS_CHOICE_SUSPENDED
        org_contact.save()

        # log suspension
        self.log_user_action(
            OrganisationAction.ACTION_MAKE_CONTACT_SUSPEND.format(
                "{} {}({})".format(
                    user.first_name,
                    user.last_name,
                    user.email,
                )
            ),
            request,
        )

        # send email
        send_organisation_contact_suspend_email_notification(
            user, request.user, self, request
        )

    @transaction.atomic
    def reinstate_user(self, user, request):
        try:
            UserDelegation.objects.get(organisation=self, user=user.id)
        except UserDelegation.DoesNotExist:
            raise ValidationError(
                f"User Delegation with user id {user.id} does not exist for organisation {self}"
            )

        # Mark organisation contact as active
        try:
            org_contact = OrganisationContact.objects.get(
                organisation=self, email=user.email
            )
        except OrganisationContact.DoesNotExist:
            raise ValidationError(
                f"Organisation Contact with email {user.email} for {self} does not exist."
            )

        org_contact.user_status = OrganisationContact.USER_STATUS_CHOICE_ACTIVE
        org_contact.save()

        # log linking
        self.log_user_action(
            OrganisationAction.ACTION_MAKE_CONTACT_REINSTATE.format(
                "{} {}({})".format(
                    user.first_name,
                    user.last_name,
                    user.email,
                )
            ),
            request,
        )
        # send email
        send_organisation_reinstate_email_notification(
            user, request.user, self, request
        )

    @property
    def name(self):
        return self.ledger_organisation_name

    @property
    def trading_name(self):
        return self.ledger_organisation_trading_name

    @property
    def abn(self):
        return self.ledger_organisation_abn

    @property
    def address(self):
        address = {
            "postal_address": self.ledger_organisation.get("postal_address", {}),
            "billing_address": self.ledger_organisation.get("billing_address", {}),
        }
        return address

    @property
    def phone_number(self):
        return self.ledger_organisation.phone_number

    @property
    def email(self):
        return self.ledger_organisation_email

    @property
    def contact_emails(self, active=True, admin=False):
        qs = self.contacts.all()
        if active:
            qs = qs.filter(user_status=OrganisationContact.USER_STATUS_CHOICE_ACTIVE)
        if admin:
            qs = qs.filter(user_role=OrganisationContact.USER_ROLE_CHOICE_ADMIN)
        return list(qs.values_list("email", flat=True).distinct())

    @property
    def first_five(self):
        first_five_delegates = self.delegates.filter(
            organisation__contacts__user_status=OrganisationContact.USER_STATUS_CHOICE_ACTIVE,
            organisation__contacts__user_role=OrganisationContact.USER_ROLE_CHOICE_ADMIN,
        ).distinct()[:5]
        return ",".join([delegate.user_full_name for delegate in first_five_delegates])

    @property
    def active_admin_users(self):
        return self.contacts.filter(
            user_status=OrganisationContact.USER_STATUS_CHOICE_ACTIVE,
            user_role=OrganisationContact.USER_ROLE_CHOICE_ADMIN,
        )

    @property
    def admin_user_count(self):
        return self.active_admin_users.count()

    @classmethod
    def organisations_user_can_admin(cls, user_id):
        return (
            cls.objects.filter(
                delegates__user=user_id,
                contacts__user=user_id,
                contacts__user_status=OrganisationContact.USER_STATUS_CHOICE_ACTIVE,
                contacts__user_role=OrganisationContact.USER_ROLE_CHOICE_ADMIN,
            )
            .distinct()
            .only("id", "ledger_organisation_name")
        )


class OrganisationContact(models.Model):
    USER_STATUS_CHOICE_DRAFT = "draft"
    USER_STATUS_CHOICE_PENDING = "pending"
    USER_STATUS_CHOICE_ACTIVE = "active"
    USER_STATUS_CHOICE_DECLINED = "declined"
    USER_STATUS_CHOICE_UNLINKED = "unlinked"
    USER_STATUS_CHOICE_SUSPENDED = "suspended"
    USER_STATUS_CHOICE_CONTACT_FORM = "contact_form"

    USER_STATUS_CHOICES = (
        (USER_STATUS_CHOICE_DRAFT, "Draft"),
        (USER_STATUS_CHOICE_PENDING, "Pending"),
        (USER_STATUS_CHOICE_ACTIVE, "Active"),
        (USER_STATUS_CHOICE_DECLINED, "Declined"),
        (USER_STATUS_CHOICE_UNLINKED, "Unlinked"),
        (USER_STATUS_CHOICE_SUSPENDED, "Suspended"),
        (
            USER_STATUS_CHOICE_CONTACT_FORM,
            "Contact Form",
        ),  # status 'contact_form' if org contact was added via 'Contact Details'
        # section in manage.vue (allows Org Contact to be distinguished from Org Delegate)
    )
    USER_ROLE_CHOICE_ADMIN = "organisation_admin"
    USER_ROLE_CHOICE_USER = "organisation_user"
    USER_ROLE_CHOICE_CONSULTANT = "consultant"

    USER_ROLE_CHOICES = (
        (USER_ROLE_CHOICE_ADMIN, "Organisation Admin"),
        (USER_ROLE_CHOICE_USER, "Organisation User"),
        (USER_ROLE_CHOICE_CONSULTANT, "Consultant"),
    )
    user = models.IntegerField(
        default=0
    )  # EmailUserRO - defaulting to 0 to allow adding non-nullable field
    user_status = models.CharField(
        "Status",
        max_length=40,
        choices=USER_STATUS_CHOICES,
        default=USER_STATUS_CHOICES[0][0],
    )
    user_role = models.CharField(
        "Role", max_length=40, choices=USER_ROLE_CHOICES, default=USER_ROLE_CHOICE_USER
    )
    organisation = models.ForeignKey(
        Organisation, related_name="contacts", on_delete=models.CASCADE
    )
    email = models.EmailField(blank=False)
    first_name = models.CharField(
        max_length=128, blank=False, verbose_name="Given name(s)"
    )
    last_name = models.CharField(max_length=128, blank=False)
    phone_number = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="phone number", help_text=""
    )
    mobile_number = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="mobile number", help_text=""
    )
    fax_number = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="fax number", help_text=""
    )

    class Meta:
        app_label = "leaseslicensing"
        unique_together = (("organisation", "email"),)
        ordering = ("organisation", "last_name", "first_name")

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.organisation})"

    @property
    def is_admin(self):
        return self.user_role == OrganisationContact.USER_ROLE_CHOICE_ADMIN

    @property
    def can_edit(self):
        """
        :return: True if the contact is in one of the editable status.
        """
        return (
            self.user_status == OrganisationContact.USER_STATUS_CHOICE_ACTIVE
            and self.user_role == OrganisationContact.USER_ROLE_CHOICE_ADMIN
        )

    @property
    def check_consultant(self):
        """
        :return: True if the contact is in one of the editable status.
        """
        return (
            self.user_status == OrganisationContact.USER_STATUS_CHOICE_ACTIVE
            and self.user_role == OrganisationContact.USER_ROLE_CHOICE_CONSULTANT
        )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class OrganisationContactDeclinedDetails(models.Model):
    request = models.ForeignKey(OrganisationContact, on_delete=models.CASCADE)
    # officer = models.ForeignKey(EmailUser, null=False, on_delete=models.CASCADE)
    officer = models.IntegerField()  # EmailUserRO

    class Meta:
        app_label = "leaseslicensing"


class UserDelegation(models.Model):
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="delegates"
    )
    user = models.IntegerField()  # EmailUserRO
    # Readonly field to store the user's full name at the time of delegation
    # handy to being able to use in the 'first_five' property without having to query ledger
    # for each user
    user_full_name = models.CharField(max_length=255, editable=False, default="")

    class Meta:
        unique_together = (("organisation", "user"),)
        app_label = "leaseslicensing"

    def __str__(self):
        return f"Org: {self.organisation}, User: {self.user}"

    def save(self, *args, **kwargs):
        email_user = retrieve_email_user(self.user)
        if email_user:
            self.user_full_name = email_user.get_full_name()

        super().save(*args, **kwargs)


class OrganisationAction(UserAction):
    ACTION_REQUEST_APPROVED = "Organisation Request {} Approved"
    ACTION_LINK = "Linked {}"
    ACTION_UNLINK = "Unlinked {}"
    ACTION_CONTACT_ADDED = "Added new contact {}"
    ACTION_CONTACT_REMOVED = "Removed contact {}"
    ACTION_CONTACT_DECLINED = "Declined contact {}"
    ACTION_MAKE_CONTACT_ADMIN = "Made contact Organisation Admin {}"
    ACTION_MAKE_CONTACT_USER = "Made contact Organisation User {}"
    # ACTION_CONTACT_REMOVED = "Removed contact {}"
    ACTION_ORGANISATIONAL_DETAILS_SAVED_NOT_CHANGED = "Details saved without changes"
    ACTION_ORGANISATIONAL_DETAILS_SAVED_CHANGED = (
        "Details saved with the following changes: \n{}"
    )
    ACTION_ORGANISATIONAL_ADDRESS_DETAILS_SAVED_NOT_CHANGED = (
        "Address Details saved without changes"
    )
    ACTION_ORGANISATIONAL_ADDRESS_DETAILS_SAVED_CHANGED = (
        "Addres Details saved with folowing changes: \n{}"
    )
    ACTION_ORGANISATION_CONTACT_ACCEPT = "Accepted contact {}"
    # ACTION_CONTACT_DECLINE = "Declined contact {}"
    ACTION_MAKE_CONTACT_SUSPEND = "Suspended contact {}"
    ACTION_MAKE_CONTACT_REINSTATE = "REINSTATED contact {}"

    ACTION_ORGANISATIONAL_DETAILS_SAVED_NOT_CHANGED = "Details saved without changes"
    ACTION_ORGANISATIONAL_DETAILS_SAVED_CHANGED = (
        "Details saved with the following changes: \n{}"
    )
    ACTION_ORGANISATIONAL_ADDRESS_DETAILS_SAVED_NOT_CHANGED = (
        "Address Details saved without changes"
    )
    ACTION_ORGANISATIONAL_ADDRESS_DETAILS_SAVED_CHANGED = (
        "Addres Details saved with folowing changes: \n{}"
    )

    ACTION_UPDATE_ORGANISATION = "Updated organisation name"
    ACTION_UPDATE_ADDRESS = "Updated address"
    ACTION_UPDATE_CONTACTS = "Updated contacts"

    @classmethod
    def log_action(cls, organisation, action, user):
        return cls.objects.create(
            organisation=organisation, who=user.id, what=str(action)
        )

    organisation = models.ForeignKey(
        Organisation, related_name="action_logs", on_delete=models.CASCADE
    )

    class Meta:
        app_label = "leaseslicensing"


def update_organisation_comms_log_filename(instance, filename):
    return "organisations/{}/communications/{}/{}".format(
        instance.log_entry.organisation.id, instance.id, filename
    )


class OrganisationLogDocument(Document):
    log_entry = models.ForeignKey(
        "OrganisationLogEntry", related_name="documents", on_delete=models.CASCADE
    )
    _file = SecureFileField(
        upload_to=update_organisation_comms_log_filename, max_length=512
    )

    class Meta:
        app_label = "leaseslicensing"


class OrganisationLogEntry(CommunicationsLogEntry):
    organisation = models.ForeignKey(
        Organisation, related_name="comms_logs", on_delete=models.CASCADE
    )

    def save(self, **kwargs):
        # save the request id if the reference not provided
        if not self.reference:
            self.reference = self.organisation.id
        super().save(**kwargs)

    class Meta:
        app_label = "leaseslicensing"


def organisation_request_identification_upload_path(instance, filename):
    if instance.id:
        return "organisation_requests/{}/{}".format(
            instance.id,
            filename,
        )
    # For the first organisation request, the instance.id is None
    # So we need to use the name to generate the path
    return "organisation_requests/{}/{}".format(
        slugify(instance.name),
        filename,
    )


class OrganisationRequest(models.Model):
    MODEL_PREFIX = "OAR"

    STATUS_CHOICE_WITH_ASSESSOR = "with_assessor"
    STATUS_CHOICE_APPROVED = "approved"
    STATUS_CHOICE_DECLINED = "declined"
    STATUS_CHOICE_UNLINKED = "unlinked"

    STATUS_CHOICES = (
        (STATUS_CHOICE_WITH_ASSESSOR, "With Assessor"),
        (STATUS_CHOICE_APPROVED, "Approved"),
        (STATUS_CHOICE_DECLINED, "Declined"),
        (STATUS_CHOICE_UNLINKED, "Unlinked"),
    )

    ROLE_CHOICE_EMPLOYEE = "employee"
    ROLE_CHOICE_CONSULTANT = "consultant"

    ROLE_CHOICES = (
        (ROLE_CHOICE_EMPLOYEE, "Employee"),
        (ROLE_CHOICE_CONSULTANT, "Consultant"),
    )
    lodgement_number = models.CharField(max_length=9, blank=True, default="")
    name = models.CharField(max_length=255, null=True, blank=True)
    organisation = models.ForeignKey(
        Organisation,
        related_name="organisation_requests",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    abn = models.CharField(max_length=50, null=True, blank=True, verbose_name="ABN")
    requester = models.IntegerField()  # EmailUserRO
    assigned_officer = models.IntegerField(null=True, blank=True)  # EmailUserRO
    identification = SecureFileField(
        upload_to=organisation_request_identification_upload_path,
        max_length=512,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default="with_assessor"
    )
    lodgement_date = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default="employee")

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["-lodgement_number"]
        verbose_name = "Organisation Request"

    def __str__(self):
        return f"{self.lodgement_number}: User {self.requester} has requested to be linked to ({self.name})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.lodgement_number:
            new_lodgment_id = f"{self.MODEL_PREFIX}{self.pk:06d}"
            self.lodgement_number = new_lodgment_id
            self.save()

    def user_has_object_permission(self, user_id):
        """Used by the secure documents api to determine if the user can view the documents"""
        return belongs_to_by_user_id(user_id, settings.GROUP_NAME_ORGANISATION_ACCESS)

    @transaction.atomic
    def accept(self, request):
        self.status = OrganisationRequest.STATUS_CHOICE_APPROVED
        self.assigned_officer = None
        self.save()
        self.log_user_action(
            OrganisationRequestUserAction.ACTION_ACCEPT_REQUEST.format(
                self.lodgement_number
            ),
            request,
        )

        ledger_org = None
        search_organisation_response = get_search_organisation(self.name, self.abn)
        if 200 == search_organisation_response["status"]:
            data = search_organisation_response["data"]
            ledger_org = data[0]

        if not ledger_org:
            # Would be much more robust if this api call gave some feedback, talk to
            # a coordinator about this
            create_organisation(self.name, self.abn)
            search_organisation_response = get_search_organisation(self.name, self.abn)
            if 200 == search_organisation_response["status"]:
                data = search_organisation_response["data"]
                ledger_org = data[0]

        org, created = Organisation.objects.get_or_create(
            ledger_organisation_id=ledger_org["organisation_id"]
        )
        if created:
            logger.info(f"Created Organisation: {org}")

        self.organisation = org
        self.save()

        delegate, created = UserDelegation.objects.get_or_create(
            user=self.requester, organisation=org
        )
        if created:
            logger.info(f"Created User Delegation: {delegate}")

        org.log_user_action(
            OrganisationAction.ACTION_REQUEST_APPROVED.format(self.lodgement_number),
            request,
        )

        delegate_email_user = retrieve_email_user(delegate.user)

        org.log_user_action(
            OrganisationAction.ACTION_LINK.format(
                "{} {}({})".format(
                    delegate_email_user.first_name,
                    delegate_email_user.last_name,
                    delegate_email_user.email,
                )
            ),
            request,
        )

        # Create contact person
        organisation_contact_role = OrganisationContact.USER_ROLE_CHOICE_ADMIN
        if self.role == OrganisationRequest.ROLE_CHOICE_CONSULTANT:
            organisation_contact_role = OrganisationContact.USER_ROLE_CHOICE_CONSULTANT

        # Create contact person
        organisation_contact, created = OrganisationContact.objects.update_or_create(
            organisation=org,
            email=delegate_email_user.email,
            defaults={
                "user": self.requester,
                "first_name": delegate_email_user.first_name,
                "last_name": delegate_email_user.last_name,
                "mobile_number": delegate_email_user.mobile_number,
                "phone_number": delegate_email_user.phone_number,
                "fax_number": delegate_email_user.fax_number,
                "user_role": organisation_contact_role,
                "user_status": OrganisationContact.USER_STATUS_CHOICE_ACTIVE,
            },
        )
        if created:
            logger.info(f"Created Organisation Contact: {organisation_contact}")

        # send email to requester
        send_organisation_request_accept_email_notification(
            self, org, delegate_email_user, request
        )

    def send_org_access_group_request_notification(self, request):
        # user submits a new organisation request
        # send email to organisation access group
        org_access_recipient_emails = []
        org_access_recipients = SystemGroupPermission.objects.filter(
            system_group__name=settings.GROUP_NAME_ORGANISATION_ACCESS
        ).only("emailuser")
        [
            org_access_recipient_emails.append(recipient.emailuser.email)
            for recipient in org_access_recipients
        ]
        send_org_access_group_request_accept_email_notification(
            self, request, org_access_recipient_emails
        )

    def assign_to(self, user_id, request):
        with transaction.atomic():
            self.assigned_officer = user_id
            self.save()
            email_user = retrieve_email_user(user_id)
            self.log_user_action(
                OrganisationRequestUserAction.ACTION_ASSIGN_TO.format(
                    email_user.get_full_name()
                ),
                request,
            )

    def unassign(self, request):
        with transaction.atomic():
            self.assigned_officer = None
            self.save()
            self.log_user_action(OrganisationRequestUserAction.ACTION_UNASSIGN, request)

    @transaction.atomic
    def decline(self, reason, request):
        self.status = OrganisationRequest.STATUS_CHOICE_DECLINED
        self.assigned_officer = None
        self.save()
        OrganisationRequestDeclinedDetails.objects.create(
            officer=request.user.id, reason=reason, organisation_request=self
        )
        self.log_user_action(
            OrganisationRequestUserAction.ACTION_DECLINE_REQUEST.format(
                self.lodgement_number
            ),
            request,
        )
        send_organisation_request_decline_email_notification(self, request)

    def send_organisation_request_email_notification(self, request):
        # user submits a new organisation request
        # send email to organisation access group
        permissions = SystemGroupPermission.objects.filter(
            system_group__name=settings.GROUP_NAME_ORGANISATION_ACCESS
        ).only("emailuser")
        org_access_recipients = [
            permission.emailuser.email for permission in permissions
        ]
        send_organisation_request_email_notification(
            self, request, org_access_recipients
        )

    def log_user_action(self, action, request):
        return OrganisationRequestUserAction.log_action(self, action, request.user.id)


class OrganisationRequestUserAction(UserAction):
    ACTION_LODGE_REQUEST = "Lodge request {}"
    ACTION_ASSIGN_TO = "Assign to {}"
    ACTION_UNASSIGN = "Unassign"
    ACTION_DECLINE_REQUEST = "Decline request {}"
    ACTION_ACCEPT_REQUEST = "Accept request {}"

    @classmethod
    def log_action(cls, request, action, user):
        return cls.objects.create(request=request, who=user, what=str(action))

    request = models.ForeignKey(
        OrganisationRequest, related_name="action_logs", on_delete=models.CASCADE
    )

    class Meta:
        app_label = "leaseslicensing"


class OrganisationRequestDeclinedDetails(models.Model):
    organisation_request = models.ForeignKey(
        OrganisationRequest, on_delete=models.CASCADE
    )
    officer = models.IntegerField()  # EmailUserRO
    reason = models.TextField(blank=True)

    class Meta:
        app_label = "leaseslicensing"


def update_organisation_request_comms_log_filename(instance, filename):
    return "organisation_requests/{}/communications/{}/{}".format(
        instance.log_entry.request.id, instance.id, filename
    )


class OrganisationRequestLogDocument(Document):
    log_entry = models.ForeignKey(
        "OrganisationRequestLogEntry",
        related_name="documents",
        on_delete=models.CASCADE,
    )
    _file = SecureFileField(
        upload_to=update_organisation_request_comms_log_filename, max_length=512
    )

    class Meta:
        app_label = "leaseslicensing"


class OrganisationRequestLogEntry(CommunicationsLogEntry):
    request = models.ForeignKey(
        OrganisationRequest, related_name="comms_logs", on_delete=models.CASCADE
    )

    def save(self, **kwargs):
        # save the request id if the reference not provided
        if not self.reference:
            self.reference = self.request.id
        super().save(**kwargs)

    class Meta:
        app_label = "leaseslicensing"
