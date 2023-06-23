import reversion
from django.apps import AppConfig
from django.conf import settings


class LeasesLicensingConfig(AppConfig):
    name = "leaseslicensing"
    verbose_name = settings.SYSTEM_NAME

    run_once = False

    def ready(self):
        if not self.run_once:
            from leaseslicensing.components.approvals.models import (
                Approval,
                ApprovalDocument,
                ApprovalType,
                ApprovalTypeDocumentType,
                ApprovalTypeDocumentTypeOnApprovalType,
            )
            from leaseslicensing.components.compliances.models import Compliance
            from leaseslicensing.components.main.models import ApplicationType
            from leaseslicensing.components.organisations import signals  # noqa
            from leaseslicensing.components.proposals import signals  # noqa
            from leaseslicensing.components.users import signals  # noqa
            from leaseslicensing.components.proposals.models import (
                AdditionalDocumentType,
                ApplicationFeeDiscount,
                ChecklistQuestion,
                CompetitiveProcess,
                Organisation,
                Proposal,
                ProposalAssessment,
                ProposalAssessmentAnswer,
                ProposalDocument,
                ProposalGeometry,
                ProposalRequirement,
                ProposalStandardRequirement,
                ProposalType,
                Referral,
                ReferralDocument,
                ReferralRecipientGroup,
                SectionChecklist,
                ShapefileDocument,
            )

            # main
            reversion.register(ApplicationType, follow=[])

            # approval
            reversion.register(
                Approval,
                follow=[
                    "licence_document",
                    "cover_letter_document",
                    "replaced_by",
                    "current_proposal",
                    "renewal_document",
                    "org_applicant",
                ],
            )
            reversion.register(ApprovalType, follow=["approvaltypedocumenttypes"])
            reversion.register(ApprovalTypeDocumentType)
            reversion.register(ApprovalTypeDocumentTypeOnApprovalType)
            reversion.register(ApprovalDocument)

            # proposal
            reversion.register(ProposalType)
            reversion.register(Organisation)
            reversion.register(ProposalDocument)
            reversion.register(CompetitiveProcess)
            reversion.register(ShapefileDocument, follow=["proposal"])
            reversion.register(AdditionalDocumentType)
            reversion.register(ApplicationFeeDiscount, follow=["proposal"])
            reversion.register(ProposalStandardRequirement, follow=["application_type"])
            reversion.register(Referral, follow=["proposal", "document"])
            reversion.register(ReferralDocument, follow=["referral"])
            reversion.register(
                ProposalRequirement,
                follow=[
                    "proposal",
                    "standard_requirement",
                    "copied_from",
                    "referral_group",
                ],
            )
            reversion.register(ReferralRecipientGroup)
            reversion.register(SectionChecklist, follow=["application_type"])
            reversion.register(ChecklistQuestion, follow=["section_checklist"])
            reversion.register(ProposalAssessment, follow=["proposal", "referral"])
            reversion.register(
                ProposalAssessmentAnswer,
                follow=["checklist_question", "proposal_assessment"],
            )
            reversion.register(
                Proposal,
                follow=[
                    "application_type",
                    "proposal_type",
                    "org_applicant",
                    "approval",
                    "previous_application",
                    "approval_level_document",
                    "generated_proposal",
                    "originating_competitive_process",
                    #  "proposalgeometry"
                ],
            )
            reversion.register(ProposalGeometry, follow=["proposal"])

            # compliance
            reversion.register(
                Compliance,
                follow=[
                    "proposal",
                    "approval",
                    "requirement",
                ],
            )

        self.run_once = True
