import json
import logging
import re

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from ledger_api_client.ledger_models import EmailUserRO as EmailUser  # , Document

from leaseslicensing.components.approvals import email as approval_email
from leaseslicensing.components.approvals.models import Approval
from leaseslicensing.components.compliances import email as compliance_email
from leaseslicensing.components.compliances.models import Compliance
from leaseslicensing.components.main.utils import (
    get_gis_data_for_proposal,
    polygon_intersects_with_layer,
)
from leaseslicensing.components.proposals import email as proposal_email
from leaseslicensing.components.proposals.email import (
    send_external_submit_email_notification,
    send_submit_email_notification,
)
from leaseslicensing.components.proposals.models import (
    AmendmentRequest,
    ProposalAct,
    ProposalAssessment,
    ProposalAssessmentAnswer,
    ProposalCategory,
    ProposalDeclinedDetails,
    ProposalDistrict,
    ProposalGeometry,
    ProposalGroup,
    ProposalIdentifier,
    ProposalLGA,
    ProposalName,
    ProposalRegion,
    ProposalTenure,
    ProposalUserAction,
    ProposalVesting,
    Referral,
)
from leaseslicensing.components.proposals.serializers import (
    ProposalAssessmentAnswerSerializer,
    ProposalGeometrySaveSerializer,
    SaveLeaseLicenceSerializer,
    SaveRegistrationOfInterestSerializer,
)
from leaseslicensing.components.tenure.models import (
    LGA,
    Act,
    Category,
    District,
    Identifier,
    Name,
    Region,
    SiteName,
    Tenure,
    Vesting,
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
    logger.debug("save_proponent_data")
    if (
        instance.application_type.name
        == settings.APPLICATION_TYPE_REGISTRATION_OF_INTEREST
    ):
        save_proponent_data_registration_of_interest(instance, request, viewset)
    elif instance.application_type.name == settings.APPLICATION_TYPE_LEASE_LICENCE:
        save_proponent_data_lease_licence(instance, request, viewset)


def save_proponent_data_registration_of_interest(instance, request, viewset):
    # proposal
    proposal_data = request.data.get("proposal") if request.data.get("proposal") else {}
    logger.debug("proposal_data = " + str(proposal_data))
    serializer = SaveRegistrationOfInterestSerializer(
        instance,
        data=proposal_data,
        context={
            "action": viewset.action,
        },
    )
    logger.debug("Validating SaveRegistrationOfInterestSerializer")
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()

    logger.debug("Saving groups data.")
    save_groups_data(instance, proposal_data["groups"])

    save_geometry(instance, request)

    populate_gis_data(instance)

    if viewset.action == "submit":
        check_geometry(instance)


def save_proponent_data_lease_licence(instance, request, viewset):
    # proposal
    proposal_data = request.data.get("proposal") if request.data.get("proposal") else {}
    logger.debug(f"proposal_data = {proposal_data}")

    serializer = SaveLeaseLicenceSerializer(
        instance,
        data=proposal_data,
        context={
            "action": viewset.action,
        },
    )
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()

    save_groups_data(instance, proposal_data["groups"])

    save_geometry(instance, request)

    populate_gis_data(instance)

    if viewset.action == "submit":
        check_geometry(instance)


def _save_answer_dict(answer_dict):
    answer_obj = ProposalAssessmentAnswer.objects.get(id=int(answer_dict["id"]))
    serializer = ProposalAssessmentAnswerSerializer(answer_obj, answer_dict)
    serializer.is_valid(raise_exception=True)
    answer_obj = serializer.save()
    return answer_obj


def save_referral_data(proposal, request, referral_completed=False):
    with transaction.atomic():
        proposal_data = (
            request.data.get("proposal") if request.data.get("proposal") else {}
        )
        if not proposal_data:
            return

        for referral in proposal_data["referrals"]:
            logger.info("Saving referral data for {}".format(referral))
            # Referee can only save changes to their own referral
            if not referral["referral"] == request.user.id:
                continue

            referral = Referral(
                pk=referral["id"],
                proposal=proposal,
                comment_map=referral["comment_map"],
                comment_proposal_details=referral["comment_proposal_details"],
                comment_proposal_impact=referral["comment_proposal_impact"],
                comment_other=referral["comment_other"],
                comment_deed_poll=referral["comment_deed_poll"],
                comment_additional_documents=referral["comment_additional_documents"],
            )
            # Only allow updating of comment fields
            referral.save(update_fields=[
                "comment_map",
                "comment_proposal_details",
                "comment_proposal_impact",
                "comment_other",
                "comment_deed_poll",
                "comment_additional_documents"]
            )


def save_assessor_data(proposal, request, viewset):
    logger.debug("save_assessor_data")
    with transaction.atomic():
        proposal_data = {}
        if request.data.get("proposal"):
            # request.data is like {'proposal': {'id': ..., ...}}
            proposal_data = request.data.get("proposal")
        else:
            # request.data is a dictionary of the proposal {'id': ..., ...}
            proposal_data = request.data

        save_site_name(proposal, proposal_data["site_name"])
        save_groups_data(proposal, proposal_data["groups"])

        # Save checklist answers
        if is_assessor(request):
            # When this assessment is for the accessing user
            if (
                "assessor_assessment" in proposal_data
                and proposal_data["assessor_assessment"]
            ):
                for section, answers in proposal_data["assessor_assessment"][
                    "section_answers"
                ].items():
                    for answer_dict in answers:
                        answer_obj = _save_answer_dict(answer_dict)
                        # Not yet sure what the intention for answer_ob is but just printing as it wasn't accessed.
                        logger.debug(answer_obj)
        # Save geometry
        save_geometry(proposal, request)
        populate_gis_data(proposal)


def check_geometry(instance):
    for geom in instance.proposalgeometry.all():
        if not geom.intersects:
            raise ValidationError(
                "One or more polygons does not intersect with a relevant layer"
            )


def save_geometry(instance, request):
    logger.debug("\n\n\nsaving geometry")

    proposal_geometry_str = request.data.get("proposal_geometry", None)
    if not proposal_geometry_str:
        logger.debug("No proposal_geometry to save")
        return

    proposal_geometry = json.loads(proposal_geometry_str)
    if 0 == len(proposal_geometry["features"]):
        logger.debug("proposal_geometry has no features to save")
        return

    proposal_geometry_ids = []
    for feature in proposal_geometry.get("features"):
        logger.debug("feature = " + str(feature))
        # check if feature is a polygon, continue if not
        if feature.get("geometry").get("type") != "Polygon":
            logger.warn(
                f"Proposal: {instance} contains a feature is not a polygon: {feature}"
            )
            continue

        # Create a Polygon object from the open layers feature
        polygon = Polygon(feature.get("geometry").get("coordinates")[0])

        # check if it intersects with any of the lands geos
        if not polygon_intersects_with_layer(
            polygon, "public:dbca_legislated_lands_and_waters"
        ):
            # if it doesn't, raise a validation error (this should be prevented in the front end
            # and is here just in case
            raise ValidationError(
                "One or more polygons do not intersect with the DBCA Lands and Waters layer"
            )

        # If it does intersect, save it and set intersects to true
        proposal_geometry_data = {
            "proposal_id": instance.id,
            "polygon": polygon,
            "intersects": True,  # probably redunant now that we are not allowing non-intersecting geometries
        }
        if feature.get("id"):
            logger.info(
                f"Updating existing proposal geometry: {feature.get('id')} for Proposal: {instance}"
            )
            try:
                proposalgeometry = ProposalGeometry.objects.get(id=feature.get("id"))
            except ProposalGeometry.DoesNotExist:
                logger.warn(f"Proposal geometry does not exist: {feature.get('id')}")
                continue
            proposal_geometry_data["drawn_by"] = proposalgeometry.drawn_by
            serializer = ProposalGeometrySaveSerializer(
                proposalgeometry, data=proposal_geometry_data
            )
        else:
            logger.info(f"Creating new proposal geometry for Proposal: {instance}")
            proposal_geometry_data["drawn_by"] = request.user.id
            serializer = ProposalGeometrySaveSerializer(data=proposal_geometry_data)

        serializer.is_valid(raise_exception=True)
        proposalgeometry_instance = serializer.save()
        logger.debug(f"Saved proposal geometry: {proposalgeometry_instance}")
        proposal_geometry_ids.append(proposalgeometry_instance.id)

    # Remove any proposal geometries from the db that are no longer in the proposal_geometry that was submitted
    deleted_proposal_geometries = (
        ProposalGeometry.objects.filter(proposal=instance)
        .exclude(id__in=proposal_geometry_ids)
        .delete()
    )
    logger.debug(f"Deleted proposal geometries: {deleted_proposal_geometries}\n\n\n")


def proposal_submit(proposal, request):
    # import ipdb; ipdb.set_trace()
    with transaction.atomic():
        if proposal.can_user_edit:
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
            if ret1 and ret2:
                proposal.processing_status = "with_assessor"
                # TODO: do we need the following 2?
                # proposal.documents.all().update(can_delete=False)
                # proposal.required_documents.all().update(can_delete=False)

                # Reason can be an object, e.g. `AmendmentReason`
                reasons = [r.reason if hasattr(r, "reason") else r for r in reasons]
                reason = ",".join(reasons)
                proposal.save(
                    version_comment=f"Requested proposal amendments done {reason}"
                )
            else:
                raise ValidationError(
                    "An error occurred while submitting proposal (Submit email notifications failed)"
                )
            # Create assessor checklist with the current assessor_list type questions
            # Assessment instance already exits then skip.
            # TODO: fix ProposalAssessment if still required
            proposal.make_questions_ready()
            # try:
            #    assessor_assessment=ProposalAssessment.objects.get
            # (proposal=proposal,referral_group=None, referral_assessment=False)
            # except ProposalAssessment.DoesNotExist:
            #    assessor_assessment=ProposalAssessment.objects.create
            # (proposal=proposal,referral_group=None, referral_assessment=False)
            #    checklist=ChecklistQuestion.objects.filter
            # (list_type='assessor_list', application_type=proposal.application_type, obsolete=False)
            #    for chk in checklist:
            #        try:
            #            chk_instance=ProposalAssessmentAnswer.objects.get
            # (question=chk, assessment=assessor_assessment)
            #        except ProposalAssessmentAnswer.DoesNotExist:
            #            chk_instance=ProposalAssessmentAnswer.objects.create
            # (question=chk, assessment=assessor_assessment)

            return proposal

        else:
            raise ValidationError("You can't edit this proposal at this moment")


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


def save_site_name(instance, site_name):
    if site_name:
        site_name, created = SiteName.objects.get_or_create(name=site_name)
        instance.site_name = site_name
        instance.save()
        logger.debug("Created new site name: " + str(site_name))


def save_groups_data(instance, groups_data):
    logger.debug("groups_data = " + str(groups_data))
    if groups_data and len(groups_data) > 0:
        group_ids = []
        for group in groups_data:
            logger.debug("group: %s", group)
            ProposalGroup.objects.get_or_create(proposal=instance, group_id=group["id"])
            logger.debug("group created")
            group_ids.append(group["id"])
        ProposalGroup.objects.filter(proposal=instance).exclude(
            group_id__in=group_ids
        ).delete()


def populate_gis_data(proposal):
    """Fetches required GIS data from KMI and saves it to the proposal
    Todo: Will need to update this to use the new KB GIS modernisation API"""
    logger.debug("-> Populating GIS data for Proposal: " + proposal.lodgement_number)
    populate_gis_data_lands_and_waters(
        proposal
    )  # Covers Identifiers, Names, Acts, Tenures and Categories
    populate_gis_data_regions(proposal)
    populate_gis_data_districts(proposal)
    populate_gis_data_lgas(proposal)
    logger.debug(
        "-> Finished populating GIS data for Proposal: " + proposal.lodgement_number
    )


def populate_gis_data_lands_and_waters(proposal):
    properties = [
        "leg_identifier",
        "leg_vesting",
        "leg_name",
        "leg_tenure",
        "leg_act",
        "category",
    ]
    gis_data_lands_and_waters = get_gis_data_for_proposal(
        proposal, "public:dbca_legislated_lands_and_waters", properties
    )
    if gis_data_lands_and_waters is None:
        logger.warn(
            "No GIS Lands and waters data found for proposal %s",
            proposal.lodgement_number,
        )
        return

    logger.debug("gis_data_lands_and_waters = " + str(gis_data_lands_and_waters))

    # This part could be refactored to be more generic
    index = 0
    if gis_data_lands_and_waters[properties[index]]:
        for identifier_name in gis_data_lands_and_waters[properties[index]]:
            if not identifier_name.strip():
                continue
            identifier, created = Identifier.objects.get_or_create(name=identifier_name)
            if created:
                logger.info(f"New Identifier created from GIS Data: {identifier}")
            ProposalIdentifier.objects.get_or_create(
                proposal=proposal, identifier=identifier
            )

    index += 1
    if gis_data_lands_and_waters[properties[index]]:
        for vesting_name in gis_data_lands_and_waters[properties[index]]:
            if not vesting_name.strip():
                continue
            vesting, created = Vesting.objects.get_or_create(name=vesting_name)
            if created:
                logger.info(f"New Vesting created from GIS Data: {vesting}")
            ProposalVesting.objects.get_or_create(proposal=proposal, vesting=vesting)

    index += 1
    if gis_data_lands_and_waters[properties[index]]:
        for name_name in gis_data_lands_and_waters[properties[index]]:
            # Yes, name_name is a pretty silly variable name, what would you call it?
            if not name_name.strip():
                continue
            name, created = Name.objects.get_or_create(name=name_name)
            if created:
                logger.info(f"New Name created from GIS Data: {name}")
            ProposalName.objects.get_or_create(proposal=proposal, name=name)

    index += 1
    if gis_data_lands_and_waters[properties[index]]:
        for tenure_name in gis_data_lands_and_waters[properties[index]]:
            if not tenure_name.strip():
                continue
            tenure, created = Tenure.objects.get_or_create(name=tenure_name)
            if created:
                logger.info(f"New Tenure created from GIS Data: {tenure}")
            ProposalTenure.objects.get_or_create(proposal=proposal, tenure=tenure)

    index += 1
    if gis_data_lands_and_waters[properties[index]]:
        for act_name in gis_data_lands_and_waters[properties[index]]:
            if not act_name.strip():
                continue
            act, created = Act.objects.get_or_create(name=act_name)
            if created:
                logger.info(f"New Act created from GIS Data: {act}")
            ProposalAct.objects.get_or_create(proposal=proposal, act=act)

    index += 1
    if gis_data_lands_and_waters[properties[index]]:
        for category_name in gis_data_lands_and_waters[properties[index]]:
            if not category_name.strip():
                continue
            category, created = Category.objects.get_or_create(name=category_name)
            if created:
                logger.info(f"New Category created from GIS Data: {category}")
            ProposalCategory.objects.get_or_create(proposal=proposal, category=category)


def populate_gis_data_regions(proposal):
    properties = [
        "drg_region_name",
    ]
    gis_data_regions = get_gis_data_for_proposal(
        proposal, "cddp:dbca_regions", properties
    )
    if gis_data_regions is None:
        logger.warn(
            "No GIS Region data found for proposal %s", proposal.lodgement_number
        )
        return

    logger.debug("gis_data_regions = " + str(gis_data_regions))

    if gis_data_regions[properties[0]]:
        for region_name in gis_data_regions[properties[0]]:
            region, created = Region.objects.get_or_create(name=region_name)
            if created:
                logger.info(f"New Region created from GIS Data: {region}")
            ProposalRegion.objects.get_or_create(proposal=proposal, region=region)


def populate_gis_data_districts(proposal):
    properties = [
        "district",
    ]
    gis_data_districts = get_gis_data_for_proposal(
        proposal, "cddp:dbca_districts", properties
    )
    if gis_data_districts is None:
        logger.warn(
            "No GIS District data found for proposal %s", proposal.lodgement_number
        )
        return

    logger.debug("gis_data_districts = " + str(gis_data_districts))

    if gis_data_districts[properties[0]]:
        for district_name in gis_data_districts[properties[0]]:
            district, created = District.objects.get_or_create(name=district_name)
            if created:
                logger.info(f"New Region created from GIS Data: {district}")
            ProposalDistrict.objects.get_or_create(proposal=proposal, district=district)


def populate_gis_data_lgas(proposal):
    properties = [
        "lga_label",
    ]
    gis_data_lgas = get_gis_data_for_proposal(
        proposal, "cddp:local_gov_authority", properties
    )
    if gis_data_lgas is None:
        logger.warn("No GIS LGA data found for proposal %s", proposal.lodgement_number)
        return

    logger.debug("gis_data_lgas = " + str(gis_data_lgas))

    if gis_data_lgas[properties[0]]:
        for lga_name in gis_data_lgas[properties[0]]:
            lga, created = LGA.objects.get_or_create(name=lga_name)
            if created:
                logger.info(f"New LGA created from GIS Data: {lga}")
            ProposalLGA.objects.get_or_create(proposal=proposal, lga=lga)
