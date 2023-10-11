import logging
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from ledger_api_client.ledger_models import EmailUserRO as EmailUser  # , Document

from leaseslicensing.components.approvals import email as approval_email
from leaseslicensing.components.approvals.models import Approval
from leaseslicensing.components.compliances import email as compliance_email
from leaseslicensing.components.compliances.models import Compliance
from leaseslicensing.components.main.utils import (
    populate_gis_data,
    save_geometry,
    save_groups_data,
    save_site_name,
)
from leaseslicensing.components.proposals import email as proposal_email
from leaseslicensing.components.proposals.email import (
    send_external_submit_email_notification,
    send_submit_email_notification,
)
from leaseslicensing.components.proposals.models import (
    AmendmentRequest,
    Proposal,
    ProposalAdditionalDocumentType,
    ProposalApplicant,
    ProposalAssessment,
    ProposalDeclinedDetails,
    ProposalGeometry,
    ProposalUserAction,
    Referral,
)
from leaseslicensing.components.proposals.serializers import (
    ProposalAssessmentSerializer,
    ProposalGeometrySerializer,
    ProposalMapFeatureInfoSerializer,
    SaveLeaseLicenceSerializer,
    SaveRegistrationOfInterestSerializer,
    SubmitLeaseLicenceSerializer,
    SubmitRegistrationOfInterestSerializer,
)
from leaseslicensing.helpers import is_assessor

logger = logging.getLogger(__name__)


def create_data_from_form(
    schema,
    post_data,
    file_data,
    post_data_index=None,
    special_fields=[],
    assessor_data=False,
):
    data = {}
    special_fields_list = []
    assessor_data_list = []
    comment_data_list = {}
    special_fields_search = SpecialFieldsSearch(special_fields)
    if assessor_data:
        assessor_fields_search = AssessorDataSearch()
        comment_fields_search = CommentDataSearch()
        for item in schema:
            data.update(_create_data_from_item(item, post_data, file_data, 0, ""))
            # _create_data_from_item(item, post_data, file_data, 0, '')
            special_fields_search.extract_special_fields(
                item, post_data, file_data, 0, ""
            )
            if assessor_data:
                assessor_fields_search.extract_special_fields(
                    item, post_data, file_data, 0, ""
                )
                comment_fields_search.extract_special_fields(
                    item, post_data, file_data, 0, ""
                )
        special_fields_list = special_fields_search.special_fields
        if assessor_data:
            assessor_data_list = assessor_fields_search.assessor_data
            comment_data_list = comment_fields_search.comment_data

    if assessor_data:
        return [data], special_fields_list, assessor_data_list, comment_data_list

    return [data], special_fields_list


def _extend_item_name(name, suffix, repetition):
    return f"{name}{suffix}-{repetition}"


def _create_data_from_item(item, post_data, file_data, repetition, suffix):
    item_data = {}

    if "name" in item:
        extended_item_name = item["name"]
    else:
        raise Exception("Missing name in item %s" % item["label"])

    if "children" not in item:
        if item["type"] in ["checkbox" "declaration"]:
            # item_data[item['name']] = post_data[item['name']]
            item_data[item["name"]] = extended_item_name in post_data
        elif item["type"] == "file":
            if extended_item_name in file_data:
                item_data[item["name"]] = str(file_data.get(extended_item_name))
                # TODO save the file here
            elif (
                extended_item_name + "-existing" in post_data
                and len(post_data[extended_item_name + "-existing"]) > 0
            ):
                item_data[item["name"]] = post_data.get(
                    extended_item_name + "-existing"
                )
            else:
                item_data[item["name"]] = ""
        else:
            if extended_item_name in post_data:
                if item["type"] == "multi-select":
                    item_data[item["name"]] = post_data.getlist(extended_item_name)
                else:
                    item_data[item["name"]] = post_data.get(extended_item_name)
    else:
        if "repetition" in item:
            item_data = generate_item_data(
                extended_item_name,
                item,
                item_data,
                post_data,
                file_data,
                len(post_data[item["name"]]),
                suffix,
            )
        else:
            item_data = generate_item_data(
                extended_item_name, item, item_data, post_data, file_data, 1, suffix
            )

    if "conditions" in item:
        for condition in item["conditions"].keys():
            for child in item["conditions"][condition]:
                item_data.update(
                    _create_data_from_item(
                        child, post_data, file_data, repetition, suffix
                    )
                )

    return item_data


def generate_item_data(
    item_name, item, item_data, post_data, file_data, repetition, suffix
):
    item_data_list = []
    for rep in range(0, repetition):
        child_data = {}
        for child_item in item.get("children"):
            child_data.update(
                _create_data_from_item(
                    child_item, post_data, file_data, 0, f"{suffix}-{rep}"
                )
            )
        item_data_list.append(child_data)

        item_data[item["name"]] = item_data_list
    return item_data


class AssessorDataSearch:
    def __init__(self, lookup_field="canBeEditedByAssessor"):
        self.lookup_field = lookup_field
        self.assessor_data = []

    def extract_assessor_data(self, item, post_data):
        values = []
        res = {"name": item, "assessor": "", "referrals": []}
        for k in post_data:
            if re.match(item, k):
                values.append({k: post_data[k]})
        if values:
            for v in values:
                for k, v in v.items():
                    parts = k.split(f"{item}-")
                    if len(parts) > 1:
                        # split parts to see if referall
                        ref_parts = parts[1].split("Referral-")
                        if len(ref_parts) > 1:
                            # Referrals
                            res["referrals"].append(
                                {
                                    "value": v,
                                    "email": ref_parts[1],
                                    "full_name": EmailUser.objects.get(
                                        email=ref_parts[1].lower()
                                    ).get_full_name(),
                                }
                            )
                        elif k.split("-")[-1].lower() == "assessor":
                            # Assessor
                            res["assessor"] = v

        return res

    def extract_special_fields(self, item, post_data, file_data, repetition, suffix):
        item_data = {}
        if "name" in item:
            extended_item_name = item["name"]
        else:
            raise Exception("Missing name in item %s" % item["label"])

        if "children" not in item:
            if "conditions" in item:
                for condition in item["conditions"].keys():
                    for child in item["conditions"][condition]:
                        item_data.update(
                            self.extract_special_fields(
                                child, post_data, file_data, repetition, suffix
                            )
                        )

            if item.get(self.lookup_field):
                self.assessor_data.append(
                    self.extract_assessor_data(extended_item_name, post_data)
                )

        else:
            if "repetition" in item:
                item_data = self.generate_item_data_special_field(
                    extended_item_name,
                    item,
                    item_data,
                    post_data,
                    file_data,
                    len(post_data[item["name"]]),
                    suffix,
                )
            else:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, 1, suffix
                )

            if "conditions" in item:
                for condition in item["conditions"].keys():
                    for child in item["conditions"][condition]:
                        item_data.update(
                            self.extract_special_fields(
                                child, post_data, file_data, repetition, suffix
                            )
                        )

        return item_data

    def generate_item_data_special_field(
        self, item_name, item, item_data, post_data, file_data, repetition, suffix
    ):
        item_data_list = []
        for rep in range(0, repetition):
            child_data = {}
            for child_item in item.get("children"):
                child_data.update(
                    self.extract_special_fields(
                        child_item, post_data, file_data, 0, f"{suffix}-{rep}"
                    )
                )
            item_data_list.append(child_data)

            item_data[item["name"]] = item_data_list
        return item_data


class CommentDataSearch:
    def __init__(self, lookup_field="canBeEditedByAssessor"):
        self.lookup_field = lookup_field
        self.comment_data = {}

    def extract_comment_data(self, item, post_data):
        res = {}
        values = []
        for k in post_data:
            if re.match(item, k):
                values.append({k: post_data[k]})
        if values:
            for v in values:
                for k, v in v.items():
                    parts = k.split(f"{item}")
                    if len(parts) > 1:
                        ref_parts = parts[1].split("-comment-field")
                        if len(ref_parts) > 1:
                            res = {f"{item}": v}
        return res

    def extract_special_fields(self, item, post_data, file_data, repetition, suffix):
        item_data = {}
        if "name" in item:
            extended_item_name = item["name"]
        else:
            raise Exception("Missing name in item %s" % item["label"])

        if "children" not in item:
            self.comment_data.update(
                self.extract_comment_data(extended_item_name, post_data)
            )

        else:
            if "repetition" in item:
                item_data = self.generate_item_data_special_field(
                    extended_item_name,
                    item,
                    item_data,
                    post_data,
                    file_data,
                    len(post_data[item["name"]]),
                    suffix,
                )
            else:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, 1, suffix
                )

        if "conditions" in item:
            for condition in item["conditions"].keys():
                for child in item["conditions"][condition]:
                    item_data.update(
                        self.extract_special_fields(
                            child, post_data, file_data, repetition, suffix
                        )
                    )

        return item_data

    def generate_item_data_special_field(
        self, item_name, item, item_data, post_data, file_data, repetition, suffix
    ):
        item_data_list = []
        for rep in range(0, repetition):
            child_data = {}
            for child_item in item.get("children"):
                child_data.update(
                    self.extract_special_fields(
                        child_item, post_data, file_data, 0, f"{suffix}-{rep}"
                    )
                )
            item_data_list.append(child_data)

            item_data[item["name"]] = item_data_list
        return item_data


class SpecialFieldsSearch:
    def __init__(self, lookable_fields):
        self.lookable_fields = lookable_fields
        self.special_fields = {}

    def extract_special_fields(self, item, post_data, file_data, repetition, suffix):
        item_data = {}
        if "name" in item:
            extended_item_name = item["name"]
        else:
            raise Exception("Missing name in item %s" % item["label"])

        if "children" not in item:
            for f in self.lookable_fields:
                if item["type"] in ["checkbox" "declaration"]:
                    val = None
                    val = item.get(f, None)
                    if val:
                        item_data[f] = extended_item_name in post_data
                        self.special_fields.update(item_data)
                else:
                    if extended_item_name in post_data:
                        val = None
                        val = item.get(f, None)
                        if val:
                            if item["type"] == "multi-select":
                                item_data[f] = ",".join(
                                    post_data.getlist(extended_item_name)
                                )
                            else:
                                item_data[f] = post_data.get(extended_item_name)
                            self.special_fields.update(item_data)
        else:
            if "repetition" in item:
                item_data = self.generate_item_data_special_field(
                    extended_item_name,
                    item,
                    item_data,
                    post_data,
                    file_data,
                    len(post_data[item["name"]]),
                    suffix,
                )
            else:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, 1, suffix
                )

        if "conditions" in item:
            for condition in item["conditions"].keys():
                for child in item["conditions"][condition]:
                    item_data.update(
                        self.extract_special_fields(
                            child, post_data, file_data, repetition, suffix
                        )
                    )

        return item_data

    def generate_item_data_special_field(
        self, item_name, item, item_data, post_data, file_data, repetition, suffix
    ):
        item_data_list = []
        for rep in range(0, repetition):
            child_data = {}
            for child_item in item.get("children"):
                child_data.update(
                    self.extract_special_fields(
                        child_item, post_data, file_data, 0, f"{suffix}-{rep}"
                    )
                )
            item_data_list.append(child_data)

            item_data[item["name"]] = item_data_list
        return item_data


def save_proponent_data(instance, request, viewset):
    if (
        instance.application_type.name
        == settings.APPLICATION_TYPE_REGISTRATION_OF_INTEREST
    ):
        save_proponent_data_registration_of_interest(instance, request, viewset)
    elif instance.application_type.name == settings.APPLICATION_TYPE_LEASE_LICENCE:
        save_proponent_data_lease_licence(instance, request, viewset)


def save_proponent_data_registration_of_interest(proposal, request, viewset):
    proposal_data = request.data.get("proposal") if request.data.get("proposal") else {}
    serializer = SaveRegistrationOfInterestSerializer(
        proposal,
        data=proposal_data,
        context={
            "action": viewset.action,
        },
    )
    if viewset.action == "submit":
        # Apply extra validation for submit
        serializer = SubmitRegistrationOfInterestSerializer(
            proposal,
            data=proposal_data,
            context={
                "action": viewset.action,
            },
        )

    geometry_data = request.data.get("proposalgeometry", None)
    if geometry_data:
        save_geometry(request, proposal, "proposals", geometry_data)

    serializer.is_valid(raise_exception=True)
    proposal = serializer.save()

    save_groups_data(proposal, proposal_data["groups"])

    populate_gis_data(proposal, "proposalgeometry")

    if viewset.action == "submit":
        check_geometry(proposal)


def save_proponent_data_lease_licence(proposal, request, viewset):
    # proposal
    proposal_data = request.data.get("proposal") if request.data.get("proposal") else {}

    serializer = SaveLeaseLicenceSerializer(
        proposal,
        data=proposal_data,
        context={
            "action": viewset.action,
        },
    )
    if viewset.action == "submit":
        # Apply extra validation for submit
        serializer = SubmitLeaseLicenceSerializer(
            proposal,
            data=proposal_data,
            context={
                "action": viewset.action,
            },
        )

    geometry_data = request.data.get("proposalgeometry", None)
    if geometry_data:
        save_geometry(request, proposal, "proposals", geometry_data)

    serializer.is_valid(raise_exception=True)
    proposal = serializer.save()

    save_groups_data(proposal, proposal_data["groups"])

    if proposal.groups.filter(group__name__iexact="tourism").exists():
        # Todo: If we need to do any specific validation of the tourism proposal details
        pass

    populate_gis_data(proposal, "proposalgeometry")

    if viewset.action == "submit":
        check_geometry(proposal)


def save_referral_data(proposal, request):
    with transaction.atomic():
        proposal_data = (
            request.data.get("proposal") if request.data.get("proposal") else {}
        )
        if not proposal_data:
            return

        referral_text = request.data.get("referral_text", None)

        for referral in proposal_data["referrals"]:
            logger.info(f"Saving referral data for {referral}")
            # Referee can only save changes to their own referral
            if not referral["referral"] == request.user.id:
                continue

            referral = Referral(
                pk=referral["id"],
                proposal=proposal,
                referral_text=referral_text,
                comment_map=referral["comment_map"],
                comment_proposal_details=referral["comment_proposal_details"],
                comment_proposal_impact=referral["comment_proposal_impact"],
                comment_gis_data=referral["comment_gis_data"],
                comment_categorisation=referral["comment_categorisation"],
                comment_deed_poll=referral["comment_deed_poll"],
                comment_additional_documents=referral["comment_additional_documents"],
            )
            # Only allow updating of comment fields
            referral.save(
                update_fields=[
                    "referral_text",
                    "comment_map",
                    "comment_proposal_details",
                    "comment_proposal_impact",
                    "comment_gis_data",
                    "comment_categorisation",
                    "comment_deed_poll",
                    "comment_additional_documents",
                ]
            )


@transaction.atomic
def save_assessor_data(proposal, request, viewset):
    proposal_data = {}
    if request.data.get("proposal"):
        # request.data is like {'proposal': {'id': ..., ...}}
        proposal_data = request.data.get("proposal")
    else:
        # request.data is a dictionary of the proposal {'id': ..., ...}
        proposal_data = request.data

    site_name = proposal_data.get("site_name", None)
    save_site_name(proposal, site_name)

    groups = proposal_data.get("groups", [])
    save_groups_data(proposal, groups)

    additional_document_types = proposal_data.get("additional_document_types", None)
    save_additional_document_types(proposal, additional_document_types)

    # Save checklist answers
    if is_assessor(request):
        if (
            "assessor_assessment" in proposal_data
            and proposal_data["assessor_assessment"]
        ):
            proposal_assessment, created = ProposalAssessment.objects.get_or_create(
                proposal=proposal
            )
            if created:
                logger.info(
                    f"Created Proposal Assessment {proposal_assessment} for {proposal}"
                )
            serializer = ProposalAssessmentSerializer(
                proposal_assessment, data=proposal_data["assessor_assessment"]
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

    # Save geometry
    geometry_data = request.data.get("proposalgeometry", None)
    if geometry_data:
        save_geometry(request, proposal, "proposals", geometry_data)

    populate_gis_data(proposal, "proposalgeometry")


def check_geometry(instance):
    for geom in instance.proposalgeometry.all():
        if not geom.intersects:
            raise ValidationError(
                "One or more polygons does not intersect with a relevant layer"
            )


@transaction.atomic
def proposal_submit(proposal, request):
    if not proposal.can_user_edit:
        raise ValidationError("You can't edit this proposal at this moment")

    proposal.submitter = request.user.id
    proposal.lodgement_date = timezone.now()
    proposal.training_completed = True
    reasons = []
    if proposal.amendment_requests:
        qs = proposal.amendment_requests.filter(status="requested")
        if qs:
            for q in qs:
                if q.reason is not None:
                    reasons.append(q.reason)
                q.status = "amended"
                q.save()

    # Create a log entry for the proposal
    proposal.log_user_action(
        ProposalUserAction.ACTION_LODGE_APPLICATION.format(proposal.id), request
    )
    # Create a log entry for the organisation
    # proposal.applicant.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(proposal.id),request)
    # applicant_field = getattr(proposal, proposal.applicant_field)
    # 20220128 Ledger to handle EmailUser logging?
    # applicant_field.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(proposal.id),request)
    # 20220128 - update ProposalAssessorGroup, ProposalApproverGroup as SystemGroups
    ret1 = send_submit_email_notification(request, proposal)
    ret2 = send_external_submit_email_notification(request, proposal)

    # proposal.save_form_tabs(request)
    if (settings.WORKING_FROM_HOME and settings.DEBUG) or ret1 and ret2:
        proposal.processing_status = "with_assessor"

        # The model returned by proposal.documents is a proposallogdocument model
        # that doesn't even have the can_delete field however Todo: We must check if there are
        # related documents fields on proposal that do have this field as we should
        # set their can_delete field as false like below as once the proposal is submitted they
        # should not be able to be deleted.
        # proposal.documents.all().update(can_delete=False)

        # Reason can be an object, e.g. `AmendmentReason`
        reasons = [r.reason if hasattr(r, "reason") else r for r in reasons]
        reason = ",".join(reasons)
        proposal.save(version_comment=f"Requested proposal amendments done {reason}")
    else:
        raise ValidationError(
            "An error occurred while submitting proposal (Submit email notifications failed)"
        )

    proposal_assessment, created = ProposalAssessment.objects.get_or_create(
        proposal=proposal
    )

    return proposal


def is_payment_officer(user):
    from leaseslicensing.components.proposals.models import PaymentOfficerGroup

    try:
        group = PaymentOfficerGroup.objects.get(default=True)
    except PaymentOfficerGroup.DoesNotExist:
        group = None
    if group:
        if user in group.members.all():
            return True
    return False


def test_proposal_emails(request):
    """Script to test all emails (listed below) from the models"""
    # setup
    if not (settings.PRODUCTION_EMAIL):
        recipients = [request.user.email]
        approval = Approval.objects.filter(migrated=False).last()
        proposal = Approval.current_proposal
        # These don't make sense, just uncommenting to get the code passing flake8
        referral = Referral.objects.last()
        amendment_request = AmendmentRequest.objects.last()
        reason = "Not enough information"
        proposal_decline = ProposalDeclinedDetails.objects.last()
        compliance = Compliance.objects.last()

        proposal_email.send_qaofficer_email_notification(
            proposal, recipients, request, reminder=False
        )
        proposal_email.send_qaofficer_complete_email_notification(
            proposal, recipients, request, reminder=False
        )
        proposal_email.send_referral_email_notification(
            referral, recipients, request, reminder=False
        )
        proposal_email.send_referral_complete_email_notification(referral, request)
        proposal_email.send_amendment_email_notification(
            amendment_request, request, proposal
        )
        proposal_email.send_submit_email_notification(request, proposal)
        proposal_email.send_external_submit_email_notification(request, proposal)
        proposal_email.send_approver_decline_email_notification(
            reason, request, proposal
        )
        proposal_email.send_approver_approve_email_notification(request, proposal)
        proposal_email.send_proposal_decline_email_notification(
            proposal, request, proposal_decline
        )
        proposal_email.send_proposal_approver_sendback_email_notification(
            request, proposal
        )
        proposal_email.send_proposal_approval_email_notification(proposal, request)

        approval_email.send_approval_expire_email_notification(approval)
        approval_email.send_approval_cancel_email_notification(approval)
        approval_email.send_approval_suspend_email_notification(approval, request)
        approval_email.send_approval_surrender_email_notification(approval, request)
        approval_email.send_approval_renewal_review_email_notification(approval)
        approval_email.send_approval_reinstate_email_notification(approval, request)

        compliance_email.send_amendment_email_notification(
            amendment_request, request, compliance, is_test=True
        )
        compliance_email.send_reminder_email_notification(compliance, is_test=True)
        compliance_email.send_internal_reminder_email_notification(
            compliance, is_test=True
        )
        compliance_email.send_due_email_notification(compliance, is_test=True)
        compliance_email.send_internal_due_email_notification(compliance, is_test=True)
        compliance_email.send_compliance_accept_email_notification(
            compliance, request, is_test=True
        )
        compliance_email.send_external_submit_email_notification(
            request, compliance, is_test=True
        )
        compliance_email.send_submit_email_notification(
            request, compliance, is_test=True
        )


def make_proposal_applicant_ready(proposal: Proposal, user: EmailUser) -> None:
    proposal_applicant, created = ProposalApplicant.objects.get_or_create(
        proposal=proposal
    )
    if created:
        proposal_applicant.emailuser_id = user.id
        proposal_applicant.email = user.email
        proposal_applicant.first_name = user.first_name
        proposal_applicant.last_name = user.last_name
        proposal_applicant.dob = user.dob

        if user.residential_address:
            proposal_applicant.residential_line1 = user.residential_address.line1
            proposal_applicant.residential_line2 = user.residential_address.line2
            proposal_applicant.residential_line3 = user.residential_address.line3
            proposal_applicant.residential_locality = user.residential_address.locality
            proposal_applicant.residential_state = user.residential_address.state
            proposal_applicant.residential_country = user.residential_address.country
            proposal_applicant.residential_postcode = user.residential_address.postcode

        if user.postal_address:
            proposal_applicant.postal_same_as_residential = (
                user.postal_same_as_residential
            )
            proposal_applicant.postal_line1 = user.postal_address.line1
            proposal_applicant.postal_line2 = user.postal_address.line2
            proposal_applicant.postal_line3 = user.postal_address.line3
            proposal_applicant.postal_locality = user.postal_address.locality
            proposal_applicant.postal_state = user.postal_address.state
            proposal_applicant.postal_country = user.postal_address.country
            proposal_applicant.postal_postcode = user.postal_address.postcode

        if user.phone_number:
            proposal_applicant.phone_number = user.phone_number

        if user.mobile_number:
            proposal_applicant.mobile_number = user.mobile_number

        proposal_applicant.save()


def get_proposal_geometries_for_map_component(proposal, context, feature_collection):
    if not feature_collection:
        feature_collection = {"type": "FeatureCollection", "features": []}

    proposal_geoms = ProposalGeometry.objects.none()
    if proposal:
        proposal_geoms = ProposalGeometry.objects.filter(proposal_id=proposal.id)

    for geom in proposal_geoms:
        g = ProposalGeometrySerializer(geom, context=context).data
        g["properties"]["source"] = "proposal"
        g["model"] = ProposalMapFeatureInfoSerializer(
            geom.proposal, context=context
        ).data
        feature_collection["features"].append(g)

    return feature_collection


def save_additional_document_types(proposal, additional_document_types):
    for document_type in additional_document_types:
        (
            additional_document_type,
            created,
        ) = ProposalAdditionalDocumentType.objects.get_or_create(
            proposal=proposal, additional_document_type_id=document_type
        )
        if created:
            logger.info(f"Created additional document type: {additional_document_type}")
    if ProposalAdditionalDocumentType.objects.filter(proposal=proposal).count() != len(
        additional_document_types
    ):
        deleted = (
            ProposalAdditionalDocumentType.objects.filter(proposal=proposal)
            .exclude(additional_document_type_id__in=additional_document_types)
            .delete()
        )
        logger.info(f"Deleted additional document types: {deleted}")
