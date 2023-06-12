<template lang="html">
    <div v-if="proposal" class="container" id="internalProposal">
        <div v-if="debug">internal/proposals/proposal.vue</div>
        <div class="row">
            <h3>{{ proposal.lodgement_number }} - {{ proposal.application_type ? proposal.application_type.name_display :
                null
            }} - {{ proposal.proposal_type ? proposal.proposal_type.description : null }}</h3>

            <div class="col-md-3">
                <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url"
                    :disable_add_entry="false" />

                <Submission v-if="canSeeSubmission" v-bind:canSeeSubmission="canSeeSubmission"
                    v-bind:showingProposal="showingProposal" :proposal="proposal"
                    :submitter_first_name="submitter_first_name" :submitter_last_name="submitter_last_name"
                    :lodgement_date="proposal.lodgement_date" @revision-to-display="revisionToDisplay" class="mt-2" />

                <Workflow ref='workflow' :proposal="proposal" :on_current_revision="on_current_revision"
                    :isFinalised="isFinalised" :canAction="canAction" :canLimitedAction="canLimitedAction"
                    :canAssess="canAssess" :can_user_edit="proposal.can_user_edit" @toggleProposal="toggleProposal"
                    @toggleRequirements="toggleRequirements" @switchStatus="switchStatus"
                    @completeReferral="completeReferral" @amendmentRequest="amendmentRequest"
                    @proposedDecline="proposedDecline" @proposedApproval="proposedApproval" @issueApproval="issueApproval"
                    @declineProposal="declineProposal" @assignRequestUser="assignRequestUser" @assignTo="assignTo"
                    @completeEditing="completeEditing" @cancelEditing="cancelEditing" class="mt-2" />
            </div>

            <div class="col-md-9">
                <!-- Main contents -->
                <template v-if="display_approval_screen">
                    <ApprovalScreen :proposal="proposal" :readonly="readonly" />
                </template>

                <template v-if="display_requirements">
                    <Requirements :proposal="proposal" :key="requirementsKey" />
                </template>

                <template v-if="(showingProposal && ['with_approver', 'approved_application', 'approved', 'declined'].
                    includes(proposal.processing_status_id)) ||
                    (canSeeSubmission && !['with_approver', 'approved_application', 'approved', 'declined'].
                        includes(proposal.processing_status_id)) ||
                    (!canSeeSubmission && showingProposal)">
                    <FormSection :formCollapse="false" label="Application" Index="application">
                        <ApplicationForm v-if="proposal" :proposal="proposal" :show_application_title="false"
                            :is_external="false" :is_internal="true" ref="application_form" :readonly="readonly"
                            :submitterId="submitter_id" :key="computedProposalId" :show_related_items_tab="true"
                            :show_additional_documents_tab="true" :registrationOfInterest="isRegistrationOfInterest"
                            :leaseLicence="isLeaseLicence" @formMounted="applicationFormMounted">
                            <!-- Inserted into the slot on the form.vue: Collapsible Assessor Questions -->
                            <template v-slot:slot_map_checklist_questions>
                                <CollapsibleQuestions component_title="Comments" ref="collapsible_map_comments"
                                    @created="collapsible_map_comments_component_mounted" class="mb-2">
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="assessor_comment_map">Assessor Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control" v-model="assessment.assessor_comment_map"
                                                id="assessor_comment_map" :readonly="!canEditComments" />
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="deficiency_comment_map">Deficiency Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control" v-model="assessment.deficiency_comment_map"
                                                id="deficiency_comment_map" :readonly="!canEditComments" />
                                        </div>
                                    </div>

                                </CollapsibleQuestions>
                                <CollapsibleQuestions component_title="Checklist Questions"
                                    ref="collapsible_map_checklist_questions"
                                    @created="collapsible_map_checklist_questions_component_mounted" class="mb-2">
                                    <template v-if="assessment_for_assessor_map.length > 0">
                                        <div class="assessment_title">Assessor</div>
                                    </template>
                                    <template v-for="question in assessment_for_assessor_map" :key="question.id">
                                        <!-- There is only one assessor assessment -->
                                        <ChecklistQuestion :question="question" />
                                    </template>

                                    <template v-for="assessment in assessments_for_referrals_map" :key="assessment.id">
                                        <!-- There can be multiple referral assessments -->
                                        <div class="assessment_title">Referral: {{ assessment.referral_fullname }}</div>
                                        <template v-for="question in assessment.answers" :key="question.id">
                                            <!-- per question -->
                                            <ChecklistQuestion :question="question" />
                                        </template>
                                    </template>
                                </CollapsibleQuestions>
                            </template>

                            <template v-slot:slot_proposal_details_checklist_questions>
                                <CollapsibleQuestions component_title="Comments" ref="collapsible_proposal_details_comments"
                                    @created="collapsible_proposal_details_comments_component_mounted" class="mb-2">
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="assessor_comment_proposal_details">Assessor Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control"
                                                v-model="assessment.assessor_comment_proposal_details"
                                                id="assessor_comment_proposal_details" :readonly="!canEditComments" />
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="deficiency_comment_proposal_details">Deficiency Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control"
                                                v-model="assessment.deficiency_comment_proposal_details"
                                                id="deficiency_comment_proposal_details" :readonly="!canEditComments" />
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="referrer_comment_proposal_details">Referrer Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control"
                                                v-model="assessment.referrer_comment_proposal_details"
                                                id="referrer_comment_proposal_details" />
                                        </div>
                                    </div>
                                </CollapsibleQuestions>
                                <CollapsibleQuestions component_title="Checklist Questions"
                                    ref="collapsible_proposal_details_checklist_questions"
                                    @created="collapsible_proposal_details_checklist_questions_component_mounted"
                                    class="mb-2">
                                    <template v-if="assessment_for_assessor_proposal_details.length > 0">
                                        <div class="assessment_title">Assessor</div>
                                    </template>
                                    <template v-for="question in assessment_for_assessor_proposal_details">
                                        <!-- There is only one assessor assessment -->
                                        <ChecklistQuestion :question="question" />
                                    </template>

                                    <template v-for="assessment in assessments_for_referrals_proposal_details">
                                        <!-- There can be multiple referral assessments -->
                                        <div class="assessment_title">Referral: {{ assessment.referral_fullname }}</div>
                                        <template v-for="question in assessment.answers"> <!-- per question -->
                                            <ChecklistQuestion :question="question" />
                                        </template>
                                    </template>
                                </CollapsibleQuestions>
                            </template>

                            <template v-slot:slot_proposal_impact_checklist_questions>
                                <CollapsibleQuestions component_title="Comments" ref="collapsible_proposal_impact_comments"
                                    @created="collapsible_proposal_impact_comments_component_mounted" class="mb-2">
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="assessor_comment_proposal_impact">Assessor Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control"
                                                v-model="assessment.assessor_comment_proposal_impact"
                                                id="assessor_comment_proposal_impact" :readonly="!canEditComments" />
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="deficiency_comment_proposal_impact">Deficiency Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control"
                                                v-model="assessment.deficiency_comment_proposal_impact"
                                                id="deficiency_comment_proposal_impact" :readonly="!canEditComments" />
                                        </div>
                                    </div>

                                </CollapsibleQuestions>
                                <CollapsibleQuestions component_title="Checklist Questions"
                                    ref="collapsible_proposal_impact_checklist_questions"
                                    @created="collapsible_proposal_impact_checklist_questions_component_mounted"
                                    class="mb-2">
                                    <template v-if="assessment_for_assessor_proposal_impact.length > 0">
                                        <div class="assessment_title">Assessor</div>
                                    </template>
                                    <template v-for="question in assessment_for_assessor_proposal_impact">
                                        <!-- There is only one assessor assessment -->
                                        <ChecklistQuestion :question="question" />
                                    </template>

                                    <template v-for="assessment in assessments_for_referrals_proposal_impact">
                                        <!-- There can be multiple referral assessments -->
                                        <div class="assessment_title">Referral: {{ assessment.referral_fullname }}</div>
                                        <template v-for="question in assessment.answers"> <!-- per question -->
                                            <ChecklistQuestion :question="question" />
                                        </template>
                                    </template>
                                </CollapsibleQuestions>
                            </template>

                            <template v-slot:slot_other_checklist_questions>
                                <CollapsibleQuestions component_title="Comments" ref="collapsible_other_comments"
                                    @created="collapsible_other_comments_component_mounted" class="mb-2">
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="assessor_comment_other">Assessor Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control" v-model="assessment.assessor_comment_other"
                                                id="assessor_comment_other" :readonly="!canEditComments" />
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="deficiency_comment_other">Deficiency Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control" v-model="assessment.deficiency_comment_other"
                                                id="deficiency_comment_other" :readonly="!canEditComments" />
                                        </div>
                                    </div>

                                </CollapsibleQuestions>
                                <CollapsibleQuestions component_title="Checklist Questions"
                                    ref="collapsible_other_checklist_questions"
                                    @created="collapsible_other_checklist_questions_component_mounted" class="mb-2">
                                    <template v-if="assessment_for_assessor_other.length > 0">
                                        <div class="assessment_title">Assessor</div>
                                    </template>
                                    <template v-for="question in assessment_for_assessor_other" :key="question.id">
                                        <!-- There is only one assessor assessment -->
                                        <ChecklistQuestion :question="question" />
                                    </template>

                                    <template v-for="assessment in assessments_for_referrals_other" :key="assessment.id">
                                        <!-- There can be multiple referral assessments -->
                                        <div class="assessment_title">Referral: {{ assessment.referral_fullname }}</div>
                                        <template v-for="question in assessment.answers" :key="question.id">
                                            <!-- per question -->
                                            <ChecklistQuestion :question="question" />
                                        </template>
                                    </template>
                                </CollapsibleQuestions>
                            </template>

                            <template v-slot:slot_deed_poll_checklist_questions>
                                <CollapsibleQuestions component_title="Comments" ref="collapsible_deed_poll_comments"
                                    @created="collapsible_deed_poll_comments_component_mounted" class="mb-2">
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="assessor_comment_deed_poll">Assessor Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control" v-model="assessment.assessor_comment_deed_poll"
                                                id="assessor_comment_deed_poll" :readonly="!canEditComments" />
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="deficiency_comment_deed_poll">Deficiency Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control" v-model="assessment.deficiency_comment_deed_poll"
                                                id="deficiency_comment_deed_poll" :readonly="!canEditComments" />
                                        </div>
                                    </div>

                                </CollapsibleQuestions>
                                <CollapsibleQuestions component_title="Checklist Questions"
                                    ref="collapsible_deed_poll_checklist_questions"
                                    @created="collapsible_deed_poll_checklist_questions_component_mounted" class="mb-2">
                                    <template v-if="assessment_for_assessor_deed_poll.length > 0">
                                        <div class="assessment_title">Assessor</div>
                                    </template>
                                    <template v-for="question in assessment_for_assessor_deed_poll" :key="question.id">
                                        <!-- There is only one assessor assessment -->
                                        <ChecklistQuestion :question="question" />
                                    </template>

                                    <template v-for="assessment in assessments_for_referrals_deed_poll"
                                        :key="assessment.id"> <!-- There can be multiple referral assessments -->
                                        <div class="assessment_title">Referral: {{ assessment.referral_fullname }}</div>
                                        <template v-for="question in assessment.answers" :key="question.id">
                                            <!-- per question -->
                                            <ChecklistQuestion :question="question" />
                                        </template>
                                    </template>
                                </CollapsibleQuestions>
                            </template>

                            <template v-slot:slot_additional_documents_checklist_questions>
                                <CollapsibleQuestions component_title="Comments"
                                    ref="collapsible_additional_documents_comments"
                                    @created="collapsible_additional_documents_comments_component_mounted" class="mb-2">
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="assessor_comment_additional_documents">Assessor Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control"
                                                v-model="assessment.assessor_comment_additional_documents"
                                                id="assessor_comment_additional_documents" :readonly="!canEditComments" />
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-2">
                                            <label for="deficiency_comment_additional_documents">Deficiency Comment</label>
                                        </div>
                                        <div class="col-md-8">
                                            <textarea class="form-control"
                                                v-model="assessment.deficiency_comment_additional_documents"
                                                id="deficiency_comment_additional_documents" :readonly="!canEditComments" />
                                        </div>
                                    </div>

                                </CollapsibleQuestions>
                                <CollapsibleQuestions component_title="Checklist Questions"
                                    ref="collapsible_additional_documents_checklist_questions"
                                    @created="collapsible_additional_documents_checklist_questions_component_mounted"
                                    class="mb-2">
                                    <template v-if="assessment_for_assessor_additional_documents.length > 0">
                                        <div class="assessment_title">Assessor</div>
                                    </template>
                                    <template v-for="question in assessment_for_assessor_additional_documents"
                                        :key="question.id"> <!-- There is only one assessor assessment -->
                                        <ChecklistQuestion :question="question" />
                                    </template>

                                    <template v-for="assessment in assessments_for_referrals_additional_documents"
                                        :key="assessment.id"> <!-- There can be multiple referral assessments -->
                                        <div class="assessment_title">Referral: {{ assessment.referral_fullname }}</div>
                                        <template v-for="question in assessment.answers" :key="question.id">
                                            <!-- per question -->
                                            <ChecklistQuestion :question="question" />
                                        </template>
                                    </template>
                                </CollapsibleQuestions>

                                <strong>Select one or more documents that need to be provided by the applicant:</strong>
                                <div v-show="select2AppliedToAdditionalDocumentTypes">
                                    <select class="form-select" ref="select_additional_document_types"></select>
                                </div>
                            </template>

                            <!-- Inserted into the slot on the form.vue: Related Items -->
                            <template v-slot:slot_section_related_items>
                                <FormSection :formCollapse="false" label="Related Items" Index="related_items">
                                    <TableRelatedItems :ajax_url="related_items_ajax_url" />
                                </FormSection>
                            </template>

                        </ApplicationForm>
                    </FormSection>
                </template>

            </div>
        </div>



        <ProposedApproval v-if="proposal" :proposal="proposal" ref="proposed_approval"
            :processing_status="proposal.processing_status" :proposal_id="proposal.id"
            :proposal_type="proposal.proposal_type ? proposal.proposal_type.code : ''"
            :isApprovalLevelDocument="isApprovalLevelDocument" :submitter_email="submitter_email"
            :applicant_email="applicant_email" :key="proposedApprovalKey" :proposedApprovalKey="proposedApprovalKey"
            :proposedApprovalState="proposedApprovalState" :assessment="assessment" />
        <ProposedDecline ref="proposed_decline" :processing_status="proposal.processing_status" :proposal="proposal"
            :proposedApprovalKey="proposedApprovalKey" />
        <AmendmentRequest ref="amendment_request" :proposal="proposal" />
        <!--
        <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
        <input type='hidden' name="schema" :value="JSON.stringify(proposal)" />
        <input type='hidden' name="proposal_id" :value="1" />
        -->
        <div v-if="displaySaveBtns" class="navbar fixed-bottom" style="background-color: #f5f5f5;">
            <div class="container">
                <div class="col-md-12 text-end">
                    <button v-if="savingProposal" type="button" class="btn btn-primary" disabled>
                        Save and Exit&nbsp;<i class="fa-solid fa-spinner fa-spin"></i>
                    </button>
                    <input v-else type="button" @click.prevent="save_and_exit" class="btn btn-primary" value="Save and Exit"
                        :disabled="disableSaveAndExitBtn" />

                    <button v-if="savingProposal" type="button" class="btn btn-primary" disabled>
                        Save and Continue&nbsp;<i class="fa-solid fa-spinner fa-spin"></i>
                    </button>
                    <input v-else type="button" @click.prevent="save_and_continue" class="btn btn-primary"
                        value="Save and Continue" :disabled="disableSaveAndContinueBtn" />
                </div>
            </div>
        </div>
    </div>
    <div v-else class="container">
        <div class="row">
            <BootstrapSpinner class="text-primary" />
        </div>
    </div>
</template>

<script>
//import ProposalDisturbance from '../../form.vue'
//import ProposalApiary from '@/components/form_apiary.vue'
//import NewApply from '../../external/proposal_apply_new.vue'
import ProposedDecline from '@/components/internal/proposals/proposal_proposed_decline.vue'
import AmendmentRequest from '@/components/internal/proposals/amendment_request.vue'
import datatable from '@vue-utils/datatable.vue'
import Requirements from '@/components/internal/proposals/proposal_requirements.vue'
import ProposedApproval from '@/components/internal/proposals/proposed_issuance.vue'
import ApprovalScreen from '@/components/internal/proposals/proposal_approval.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import Submission from '@common-utils/submission.vue'
import Workflow from '@common-utils/workflow.vue'
import { api_endpoints, helpers, constants } from '@/utils/hooks'
import ApplicationForm from '@/components/form.vue';
import FormSection from "@/components/forms/section_toggle.vue"
import CollapsibleQuestions from '@/components/forms/collapsible_component.vue'
import ChecklistQuestion from '@/components/common/component_checklist_question.vue'
import TableRelatedItems from '@/components/common/table_related_items.vue'
require("select2/dist/css/select2.min.css");
// CSS definitions to make sure workflow swal2 popovers are placed above any open bootstrap popover
// See: `swal.fire` `customClass` property
require("../../../../../../static/leaseslicensing/css/workflow.css")

export default {
    name: 'InternalProposal',
    data: function () {
        let vm = this;
        return {
            detailsBody: 'detailsBody' + vm._.uid,
            addressBody: 'addressBody' + vm._.uid,
            contactsBody: 'contactsBody' + vm._.uid,
            siteLocations: 'siteLocations' + vm._.uid,
            related_items_datatable_id: 'related_items_datatable' + vm._.uid,
            defaultKey: "aho",
            proposal: null,
            savingProposal: false,
            latest_revision: {},
            current_revision_id: null,
            assessment: {},
            "loading": [],
            //selected_referral: '',
            //referral_text: '',
            approver_comment: '',
            form: null,
            members: [],
            //department_users : [],
            contacts_table_initialised: false,
            initialisedSelects: false,
            showingProposal: false,
            showingRequirements: false,
            hasAmendmentRequest: false,
            //requirementsComplete:true,
            state_options: ['requirements', 'processing'],
            contacts_table_id: vm._.uid + 'contacts-table',
            contacts_options: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                ajax: {
                    "url": vm.contactsURL,
                    "dataSrc": ''
                },
                columns: [
                    {
                        title: 'Name',
                        mRender: function (data, type, full) {
                            return full.first_name + " " + full.last_name;
                        }
                    },
                    {
                        title: 'Phone',
                        data: 'phone_number'
                    },
                    {
                        title: 'Mobile',
                        data: 'mobile_number'
                    },
                    {
                        title: 'Fax',
                        data: 'fax_number'
                    },
                    {
                        title: 'Email',
                        data: 'email'
                    },
                ],
                processing: true
            },
            contacts_table: null,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            //comms_url: helpers.add_endpoint_json(api_endpoints.proposals, vm.$route.params.proposal_id + '/comms_log'),
            //comms_add_url: helpers.add_endpoint_json(api_endpoints.proposals, vm.$route.params.proposal_id + '/add_comms_log'),
            //logs_url: helpers.add_endpoint_json(api_endpoints.proposals, vm.$route.params.proposal_id + '/action_log'),
            comms_url: helpers.add_endpoint_json(api_endpoints.proposal, vm.$route.params.proposal_id + '/comms_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.proposal, vm.$route.params.proposal_id + '/add_comms_log'),
            logs_url: helpers.add_endpoint_json(api_endpoints.proposal, vm.$route.params.proposal_id + '/action_log'),
            panelClickersInitialised: false,
            //sendingReferral: false,
            uuid: 0,
            //additional_document_types: [],
            additionalDocumentTypesSelected: [],
            select2AppliedToAdditionalDocumentTypes: false,
            proposedApprovalState: ""
        }
    },
    components: {
        //ProposalDisturbance,
        //ProposalApiary,
        datatable,
        ProposedDecline,
        AmendmentRequest,
        Requirements,
        ProposedApproval,
        ApprovalScreen,
        CommsLogs,
        Submission,
        Workflow,
        //MoreReferrals,
        //NewApply,
        //MapLocations,
        ApplicationForm,
        FormSection,
        CollapsibleQuestions,
        ChecklistQuestion,
        TableRelatedItems,
    },
    props: {
        proposalId: {
            type: Number,
        },
    },
    watch: {

    },
    computed: {
        related_items_ajax_url: function () {
            return '/api/proposal/' + this.proposal.id + '/related_items/'
        },
        requirementsKey: function () {
            const req = "proposal_requirements_" + this.uuid;
            return req;
        },
        canEditComments: function () {
            let canEdit = false;
            if ([constants.PROPOSAL_STATUS.WITH_ASSESSOR.ID, constants.PROPOSAL_STATUS.WITH_ASSESSOR_CONDITIONS.ID].includes(this.proposal.processing_status_id)) {
                if (this.proposal.application_type.name === constants.APPLICATION_TYPES.LEASE_LICENCE) {
                    if (this.proposal.accessing_user_roles.includes(constants.ROLES.LEASE_LICENCE_ASSESSOR.ID)) {
                        canEdit = true;
                    }
                } else if (this.proposal.application_type.name === constants.APPLICATION_TYPES.REGISTRATION_OF_INTEREST) {
                    if (this.proposal.accessing_user_roles.includes(constants.ROLES.REGISTRATION_OF_INTEREST_ASSESSOR.ID)) {
                        canEdit = true;
                    }
                }
            }
            return canEdit;
        },
        displaySaveBtns: function () {
            let display = false

            if ([constants.PROPOSAL_STATUS.WITH_ASSESSOR.ID, constants.PROPOSAL_STATUS.WITH_ASSESSOR_CONDITIONS.ID].includes(this.proposal.processing_status_id)) {
                if (this.proposal.application_type.name === constants.APPLICATION_TYPES.LEASE_LICENCE) {
                    if (this.proposal.accessing_user_roles.includes(constants.ROLES.LEASE_LICENCE_ASSESSOR.ID)) {
                        display = true
                    }
                } else if (this.proposal.application_type.name === constants.APPLICATION_TYPES.REGISTRATION_OF_INTEREST) {
                    if (this.proposal.accessing_user_roles.includes(constants.ROLES.REGISTRATION_OF_INTEREST_ASSESSOR.ID)) {
                        display = true
                    }
                }
            } else if ([constants.PROPOSAL_STATUS.WITH_REFERRAL.ID, constants.PROPOSAL_STATUS.WITH_REFERRAL_CONDITIONS.ID].includes(this.proposal.processing_status_id)) {
                if (this.proposal.accessing_user_roles.includes(constants.ROLES.REFERRAL.ID)) {
                    display = true
                }
            } else if ([constants.PROPOSAL_STATUS.APPROVED_EDITING_INVOICING.ID].includes(this.proposal.processing_status_id)) {
                if (this.proposal.accessing_user_roles.includes(constants.ROLES.FINANCE.ID)) {
                    display = true
                }
            }

            return display
        },
        disableSaveAndContinueBtn: function () {  // Is this needed?
            return !this.displaySaveBtns
        },
        disableSaveAndExitBtn: function () {  // Is this needed?
            return !this.displaySaveBtns
        },
        submitter_first_name: function () {
            if (this.proposal.submitter) {
                return this.proposal.submitter.first_name
            } else {
                return ''
            }
        },
        submitter_last_name: function () {
            if (this.proposal.submitter) {
                return this.proposal.submitter.last_name
            } else {
                return ''
            }
        },
        submitter_id: function () {
            if (this.proposal.submitter) {
                return this.proposal.submitter.id
            } else {
                return this.proposal.applicant_obj.id
            }
        },
        submitter_email: function () {
            if (this.proposal.submitter) {
                return this.proposal.submitter.email
            } else {
                return this.proposal.applicant_obj.email
            }
        },
        proposal_form_url: function () {
            if ([constants.PROPOSAL_STATUS.WITH_ASSESSOR.ID, constants.PROPOSAL_STATUS.WITH_ASSESSOR_CONDITIONS.ID].includes(this.proposal.processing_status_id)) {
                return `/api/proposal/${this.proposal.id}/assessor_save.json`
            } else if ([constants.PROPOSAL_STATUS.WITH_REFERRAL.ID, constants.PROPOSAL_STATUS.WITH_REFERRAL_CONDITIONS.ID].includes(this.proposal.processing_status_id)) {
                return `/api/proposal/${this.proposal.id}/referral_save.json`
            } else if ([constants.PROPOSAL_STATUS.APPROVED_EDITING_INVOICING.ID,].includes(this.proposal.processing_status_id)) {
                return `/api/proposal/${this.proposal.id}/finance_save.json`
            } else {
                // Should not reach here
                return ''
            }
        },
        complete_referral_url: function () {
            return `/api/proposal/${this.proposal.id}/complete_referral.json`
        },
        isRegistrationOfInterest: function () {
            return this.proposal.application_type.name === constants.APPLICATION_TYPES.REGISTRATION_OF_INTEREST ? true : false
        },
        isLeaseLicence: function () {
            return this.proposal.application_type.name === constants.APPLICATION_TYPES.LEASE_LICENCE ? true : false
        },
        assessment_for_assessor_map: function () {
            try {
                let answers = this.proposal.assessor_assessment.section_answers.map // This may return undefined
                return answers ? answers : []  // Check if it's undefined
            } catch (err) {
                return []
            }
        },
        assessment_for_assessor_proposal_details: function () {
            try {
                let answers = this.proposal.assessor_assessment.section_answers.proposal_details
                return answers ? answers : []
            } catch (err) {
                return []
            }
        },
        assessment_for_assessor_proposal_impact: function () {
            try {
                let answers = this.proposal.assessor_assessment.section_answers.proposal_impact
                return answers ? answers : []
            } catch (err) {
                return []
            }
        },
        assessment_for_assessor_other: function () {
            try {
                let answers = this.proposal.assessor_assessment.section_answers.other
                return answers ? answers : []
            } catch (err) {
                return []
            }
        },
        assessment_for_assessor_deed_poll: function () {
            try {
                let answers = this.proposal.assessor_assessment.section_answers.deed_poll
                return answers ? answers : []
            } catch (err) {
                return []
            }
        },
        assessment_for_assessor_additional_documents: function () {
            try {
                let answers = this.proposal.assessor_assessment.section_answers.additional_documents
                return answers ? answers : []
            } catch (err) {
                return []
            }
        },
        assessments_for_referrals_map: function () {
            try {
                let assessments = []
                for (let assessment of this.proposal.referral_assessments) {
                    if (assessment.section_answers.map) {  // Check if this is undefined
                        let my_assessment = {
                            'referral_fullname': assessment.referral.referral.fullname,
                            'answers': assessment.section_answers.map
                        }
                        assessments.push(my_assessment)
                    }
                }
                return assessments
            } catch (err) {
                return []
            }
        },
        assessments_for_referrals_proposal_details: function () {
            try {
                let assessments = []
                for (let assessment of this.proposal.referral_assessments) {
                    if (assessment.section_answers.proposal_details) {
                        let my_assessment = {
                            'referral_fullname': assessment.referral.referral.fullname,
                            'answers': assessment.section_answers.proposal_details
                        }
                        assessments.push(my_assessment)
                    }
                }
                return assessments
            } catch (err) {
                return []
            }
        },
        assessments_for_referrals_proposal_impact: function () {
            try {
                let assessments = []
                for (let assessment of this.proposal.referral_assessments) {
                    if (assessment.section_answers.proposal_impact) {
                        let my_assessment = {
                            'referral_fullname': assessment.referral.referral.fullname,
                            'answers': assessment.section_answers.proposal_impact
                        }
                        assessments.push(my_assessment)
                    }
                }
                return assessments
            } catch (err) {
                return []
            }
        },
        assessments_for_referrals_other: function () {
            try {
                let assessments = []
                for (let assessment of this.proposal.referral_assessments) {
                    if (assessment.section_answers.other) {
                        let my_assessment = {
                            'referral_fullname': assessment.referral.referral.fullname,
                            'answers': assessment.section_answers.other
                        }
                        assessments.push(my_assessment)
                    }
                }
                return assessments
            } catch (err) {
                return []
            }
        },
        assessments_for_referrals_deed_poll: function () {
            try {
                let assessments = []
                for (let assessment of this.proposal.referral_assessments) {
                    if (assessment.section_answers.deed_poll) {
                        let my_assessment = {
                            'referral_fullname': assessment.referral.referral.fullname,
                            'answers': assessment.section_answers.deed_poll
                        }
                        assessments.push(my_assessment)
                    }
                }
                return assessments
            } catch (err) {
                return []
            }
        },
        assessments_for_referrals_additional_documents: function () {
            try {
                let assessments = []
                for (let assessment of this.proposal.referral_assessments) {
                    if (assessment.section_answers.additional_documents) {
                        let my_assessment = {
                            'referral_fullname': assessment.referral.referral.fullname,
                            'answers': assessment.section_answers.additional_documents
                        }
                        assessments.push(my_assessment)
                    }
                }
                return assessments
            } catch (err) {
                return []
            }
        },
        proposedApprovalKey: function () {
            return "proposed_approval_" + this.uuid;
        },
        computedProposalId: function () {
            if (this.proposal) {
                // Create a new key to make vue reload the component
                return `${this.proposal.id}-${this.uuid}`;
            }
        },
        debug: function () {
            if (this.$route.query.debug) {
                return this.$route.query.debug === 'true'
            }
            return false
        },
        display_approval_screen: function () {
            if (this.debug)
                return true
            let ret_val =
                this.proposal.processing_status_id == constants.PROPOSAL_STATUS.WITH_APPROVER.ID ||
                this.proposal.processing_status_id == constants.PROPOSAL_STATUS.APPROVED_EDITING_INVOICING.ID ||
                this.proposal.processing_status_id == constants.PROPOSAL_STATUS.APPROVED_COMPETITIVE_PROCESS.ID ||
                this.isFinalised
            return ret_val
        },
        display_requirements: function () {
            let ret_val =
                this.proposal.processing_status_id == constants.PROPOSAL_STATUS.WITH_ASSESSOR_CONDITIONS.ID ||
                this.proposal.processing_status_id == constants.PROPOSAL_STATUS.WITH_REFERRAL_CONDITIONS.ID ||
                ((this.proposal.processing_status_id == constants.PROPOSAL_STATUS.WITH_APPROVER.ID || this.isFinalised) && this.showingRequirements)
            return ret_val
        },
        /*
        showElectoralRoll: function(){
            // TODO: implement
            return true
        },
        */
        showElectoralRoll: function () {
            let show = false;
            if (this.proposal && ['wla', 'mla'].includes(this.proposal.application_type_code)) {
                show = true;
            }
            return show;
        },
        readonly: function () {
            return true
        },
        contactsURL: function () {
            return this.proposal != null ? helpers.add_endpoint_json(api_endpoints.organisations, this.proposal.applicant.id + '/contacts') : '';
        },
        isLoading: function () {
            return this.loading.length > 0
        },
        csrf_token: function () {
            return helpers.getCookie('csrftoken')
        },
        isFinalised: function () {
            return (this.proposal.processing_status == 'Declined' ||
                this.proposal.processing_status == 'Approved' ||
                this.proposal.processing_status_id == constants.PROPOSAL_STATUS.APPROVED_APPLICATION.ID //approved_application
            );
        },
        canAssess: function () {
            return true  // TODO: Implement correctly.  May not be needed though

            //return this.proposal && this.proposal.assessor_mode.assessor_can_assess ? true : false;
        },
        hasAssessorMode: function () {
            return this.proposal && this.proposal.assessor_mode.has_assessor_mode ? true : false;
        },
        canAction: function () {

            // For now returning true when viewing the current version of the Proposal
            return this.on_current_revision;  // TODO: implement this.  This is just temporary solution

            //if (this.proposal.processing_status == 'With Approver'){
            //    return this.proposal && (this.proposal.processing_status == 'With Approver' || this.proposal.processing_status == 'With Assessor' || this.proposal.processing_status == 'With Assessor (Requirements)') && !this.isFinalised && !this.proposal.can_user_edit && (this.proposal.current_assessor.id == this.proposal.assigned_approver || this.proposal.assigned_approver == null ) && this.proposal.assessor_mode.assessor_can_assess? true : false;
            //}
            //else{
            //    return this.proposal && (this.proposal.processing_status == 'With Approver' || this.proposal.processing_status == 'With Assessor' || this.proposal.processing_status == 'With Assessor (Requirements)') && !this.isFinalised && !this.proposal.can_user_edit && (this.proposal.current_assessor.id == this.proposal.assigned_officer || this.proposal.assigned_officer == null ) && this.proposal.assessor_mode.assessor_can_assess? true : false;
            //}
        },
        canLimitedAction: function () {

            // For now returning true when viewing the current version of the Proposal
            return this.on_current_revision;  // TODO: implement this.  This is just temporary solution

            //    if (this.proposal.processing_status == 'With Approver'){
            //        return
            //            this.proposal
            //            && (
            //                this.proposal.processing_status == 'With Assessor' ||
            //                //this.proposal.processing_status == 'With Referral' ||
            //                this.proposal.processing_status == 'With Assessor (Requirements)'
            //            )
            //            && !this.isFinalised && !this.proposal.can_user_edit
            //            && (
            //                this.proposal.current_assessor.id == this.proposal.assigned_approver ||
            //                this.proposal.assigned_approver == null
            //            ) && this.proposal.assessor_mode.assessor_can_assess? true : false;
            //    }
            //    else{
            //        return
            //            this.proposal
            //            && (
            //                this.proposal.processing_status == 'With Assessor' ||
            //                //this.proposal.processing_status == 'With Referral' ||
            //                this.proposal.processing_status == 'With Assessor (Requirements)'
            //            ) && !this.isFinalised && !this.proposal.can_user_edit
            //            && (
            //                this.proposal.current_assessor.id == this.proposal.assigned_officer ||
            //                this.proposal.assigned_officer == null
            //            ) && this.proposal.assessor_mode.assessor_can_assess? true : false;
            //    }
        },
        canSeeSubmission: function () {
            //return this.proposal && (this.proposal.processing_status != 'With Assessor (Requirements)' && this.proposal.processing_status != 'With Approver' && !this.isFinalised)
            return this.proposal && ![
                'With Assessor (Requirements)', // FIXME What is this processing status for?
                constants.PROPOSAL_STATUS.WITH_ASSESSOR_CONDITIONS.TEXT,
                constants.PROPOSAL_STATUS.WITH_REFERRAL_CONDITIONS.TEXT,
            ].includes(this.proposal.processing_status)
        },
        on_current_revision: function () {
            // Returns whether the currently displayed version is the latest one
            return this.latest_revision.revision_id === this.current_revision_id;
        },
        isApprovalLevelDocument: function () {
            return this.proposal && this.proposal.processing_status == 'With Approver' && this.proposal.approval_level != null && this.proposal.approval_level_document == null ? true : false;
        },
        applicant_email: function () {
            return this.proposal && this.proposal.applicant.email ? this.proposal.applicant.email : '';
        },
    },
    methods: {
        completeEditing: async function () {
            let vm = this
            let payload = { 'proposal': this.proposal }

            const res = await fetch('/api/proposal/' + this.proposal.id + '/finance_complete_editing.json', { body: JSON.stringify(payload), method: 'POST' })

            if (res.ok) {
                await swal.fire({
                    title: 'Saved',
                    text: 'Your proposal has been saved',
                    icon: 'success',
                })
            } else {
                let errors = [];
                await res.json().then(json => {
                    for (var key in json) {
                        errors.push(`${key}: ${typeof (json[key]) == 'string' ? json[key] : json[key].join(",")}`)
                    }
                    swal.fire({
                        title: "Please fix following errors before saving",
                        text: errors.join(","),
                        icon: 'error',
                    })
                })
            }
        },
        cancelEditing: function () {
            alert('cancelEditing')
        },
        applicationFormMounted: function () {
            this.fetchAdditionalDocumentTypesDict()  // <select> element for the additional document type exists in the ApplicationForm component, which is a child component of this component.
            // Therefore to apply select2 to the element inside child component, we have to make sure the childcomponent has been mounted.  Then select2 can be applied.
        },
        applySelect2ToAdditionalDocumentTypes: function (option_data) {
            let vm = this

            if (!vm.select2AppliedToAdditionalDocumentTypes) {
                $(vm.$refs.select_additional_document_types).select2({
                    "theme": "bootstrap-5",
                    allowClear: false,
                    placeholder: "Select Type",
                    multiple: true,
                    data: option_data,
                }).
                    on('select2:select', function (e) {
                        //vm.updateApplicationTypeFilterCache()
                        //vm.main_manager.show_me()
                    }).
                    on('select2:unselect', function (e) {
                        //vm.updateApplicationTypeFilterCache()
                        //vm.main_manager.show_me()
                    })
                vm.select2AppliedToAdditionalDocumentTypes = true
            }

            // Set default selections
            //$(vm.$refs.select_additional_document_types).val(vm.additionalDocumentTypesSelected).trigger('change')
        },
        addEventListeners: function () {
        },
        /*
        applySelect2ToAdditionalDocumentType: function(option_data){
            let vm = this
            vm.additional_document_types = option_data

            // TODO: Make select2 work...  Somehow the code below doesn't work...

            $(vm.$refs.selectAdditionalDocumentTypes).select2({
                "theme": "bootstrap-5",
                allowClear: true,
                placeholder: "Select Document Type(s)",
                multiple: true,
                minimumResultsForSearch: -1,  // This hide the search box below selections
            //    data: option_data,
            })
            vm.select2AppliedToAdditionalDocumentTypes = true
        },
        */
        collapsible_map_checklist_questions_component_mounted: function () {
            this.$refs.collapsible_map_checklist_questions.show_warning_icon(false)
        },
        collapsible_other_checklist_questions_component_mounted: function () {
            this.$refs.collapsible_other_checklist_questions.show_warning_icon(false)
        },
        collapsible_deed_poll_checklist_questions_component_mounted: function () {
            this.$refs.collapsible_deed_poll_checklist_questions.show_warning_icon(false)
        },
        collapsible_additional_documents_checklist_questions_component_mounted: function () {
            this.$refs.collapsible_additional_documents_checklist_questions.show_warning_icon(false)
        },
        collapsible_proposal_details_checklist_questions_component_mounted: function () {
            this.$refs.collapsible_proposal_details_checklist_questions.show_warning_icon(false)
        },
        collapsible_proposal_impact_checklist_questions_component_mounted: function () {
            this.$refs.collapsible_proposal_impact_checklist_questions.show_warning_icon(false)
        },
        collapsible_map_comments_component_mounted: function () {
            this.$refs.collapsible_map_comments.show_warning_icon(false)
        },
        collapsible_other_comments_component_mounted: function () {
            this.$refs.collapsible_other_comments.show_warning_icon(false)
        },
        collapsible_deed_poll_comments_component_mounted: function () {
            this.$refs.collapsible_deed_poll_comments.show_warning_icon(false)
        },
        collapsible_additional_documents_comments_component_mounted: function () {
            this.$refs.collapsible_additional_documents_comments.show_warning_icon(false)
        },
        collapsible_proposal_details_comments_component_mounted: function () {
            this.$refs.collapsible_proposal_details_comments.show_warning_icon(false)
        },
        collapsible_proposal_impact_comments_component_mounted: function () {
            this.$refs.collapsible_proposal_impact_comments.show_warning_icon(false)
        },
        locationUpdated: function () {
            console.log('in locationUpdated()');
        },
        save_and_continue: async function () {
            this.savingProposal = true;
            await this.save().then(() => {
                this.savingProposal = false;
            });
        },
        save_and_exit: async function () {
            await this.save_and_continue().then(() => {
                this.$router.push({ name: 'internal-dashboard' });
            });
        },
        completeReferral: async function () {
            let vm = this;
            vm.checkAssessorData();
            swal.fire({
                title: "Complete Referral",
                text: "Are you sure you want to complete this referral?",
                icon: "question",
                showCancelButton: true,
                confirmButtonText: 'Submit',
                customClass: {
                    container: 'swal2-popover'
                }
            }).then(async (result) => {
                if (result.isConfirmed) {
                    const res_save_data = await fetch(
                        vm.complete_referral_url,
                        {
                            body: JSON.stringify({ 'proposal': this.proposal }),
                            method: 'POST',
                            headers: {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                            },
                        }
                    )
                    // Get the id of the referral popover and hide it
                    let modal_id = $(
                        vm.$refs.workflow.$refs.more_referrals.$refs.showRef).attr(
                            "aria-describedby");
                    $(`#${modal_id}`).hide();

                    this.$router.push({ name: 'internal-dashboard' })
                }
            }).catch(err => {
                swal.fire({
                    title: 'Referral Error',
                    text: err["message"],
                    icon: 'error',
                    customClass: {
                        container: 'swal2-popover'
                    }
                })
            });
        },
        save: async function () {
            let vm = this;
            vm.checkAssessorData();
            try {
                let payload = { 'proposal': this.proposal }
                // When in Entering Conditions status ApplicationForm might not be there
                if (vm.$refs.application_form && vm.$refs.application_form.$refs.component_map) {
                    payload['proposal_geometry'] = vm.$refs.application_form.$refs.component_map.getJSONFeatures();
                }

                const res = await fetch(vm.proposal_form_url, { body: JSON.stringify(payload), method: 'POST' })

                if (res.ok) {
                    swal.fire({
                        title: 'Saved',
                        text: 'Your proposal has been saved',
                        icon: 'success',
                    }).then(async () => {
                        let resData = await res.json();
                        vm.proposal = Object.assign({}, resData);
                        vm.$nextTick(async () => {
                            if (vm.$refs.application_form != undefined) {
                                vm.$refs.application_form.incrementComponentMapKey();
                            }
                        });
                    })
                } else {
                    let err = await res.json()
                    await swal.fire({
                        title: "Please fix following errors before saving",
                        text: JSON.stringify(err),
                        icon: 'error',
                    })
                }
            } catch (err) {
                console.error(err)
            }
        },
        checkAssessorData: function () {
            //check assessor boxes and clear value of hidden assessor boxes so it won't get printed on approval pdf.

            //select all fields including hidden fields
            //console.log("here");
            var all_fields = $('input[type=text]:required, textarea:required, input[type=checkbox]:required, input[type=radio]:required, input[type=file]:required, select:required')

            all_fields.each(function () {
                var ele = null;
                //check the fields which has assessor boxes.
                ele = $("[name=" + this.name + "-Assessor]");
                if (ele.length > 0) {
                    var visiblity = $("[name=" + this.name + "-Assessor]").is(':visible')
                    if (!visiblity) {
                        if (ele[0].value != '') {
                            //console.log(visiblity, ele[0].name, ele[0].value)
                            ele[0].value = ''
                        }
                    }
                }
            });
        },
        initialiseOrgContactTable: function () {
            let vm = this;
            if (vm.proposal && !vm.contacts_table_initialised) {
                vm.contacts_options.ajax.url = helpers.add_endpoint_json(api_endpoints.organisations, vm.proposal.applicant.id + '/contacts');
                vm.contacts_table = $('#' + vm.contacts_table_id).DataTable(vm.contacts_options);
                vm.contacts_table_initialised = true;
            }
        },
        commaToNewline(s) {
            return s.replace(/[,;]/g, '\n');
        },
        proposedDecline: function () {
            this.uuid++;
            //this.$refs.proposed_decline.decline = this.proposal.proposaldeclineddetails != null ? Object.assign({}, this.proposal.proposaldeclineddetails): {};
            this.$nextTick(() => {
                this.$refs.proposed_decline.isModalOpen = true;
            });
        },
        proposedApproval: function () {
            this.proposedApprovalState = 'proposed_approval';
            // this.uuid++; Why do we need to reload the whole form when we open a modal!?
            this.$nextTick(() => {
                //this.$refs.proposed_approval.approval = this.proposal.proposed_issuance_approval != null ? Object.assign({}, this.proposal.proposed_issuance_approval) : {};
                this.$refs.proposed_approval.isModalOpen = true;
            });
        },
        issueApproval: function () {
            //this.$refs.proposed_approval.approval = helpers.copyObject(this.proposal.proposed_issuance_approval);

            //save approval level comment before opening 'issue approval' modal
            if (this.proposal && this.proposal.processing_status == 'With Approver' && this.proposal.approval_level != null && this.proposal.approval_level_document == null) {
                if (this.proposal.approval_level_comment != '') {
                    let vm = this;
                    let data = new FormData();
                    data.append('approval_level_comment', vm.proposal.approval_level_comment)
                    fetch(helpers.add_endpoint_json(api_endpoints.proposal, vm.proposal.id + '/approval_level_comment'), { body: JSON.stringify(data), method: 'POST' }).then(
                        res => {
                            vm.proposal = res.body;
                            //vm.refreshFromResponse(res);
                        }, err => {
                            console.log(err);
                        }
                    );
                }
            }
            if (this.isApprovalLevelDocument && this.proposal.approval_level_comment == '') {
                swal(
                    'Error',
                    'Please add Approval document or comments before final approval',
                    'error'
                )
            } else {
                this.proposedApprovalState = 'final_approval';
                // this.uuid++; Why do we need to reload the whole form when we open a modal!?
                this.$nextTick(() => {
                    //this.$refs.proposed_approval.approval = this.proposal.proposed_issuance_approval != null ? helpers.copyObject(this.proposal.proposed_issuance_approval) : {};
                    //this.$refs.proposed_approval.isApprovalLevelDocument = this.isApprovalLevelDocument;
                    this.$refs.proposed_approval.isModalOpen = true;
                });
            }

        },
        declineProposal: function () {
            this.$refs.proposed_decline.decline = this.proposal.proposaldeclineddetails != null ? helpers.copyObject(this.proposal.proposaldeclineddetails) : {};
            this.$refs.proposed_decline.isModalOpen = true;
        },
        amendmentRequest: function () {
            let values = '';
            $('.deficiency').each((i, d) => {
                values += $(d).val() != '' ? `Question - ${$(d).data('question')}\nDeficiency - ${$(d).val()}\n\n` : '';
            });
            //this.deficientFields();
            this.$refs.amendment_request.amendment.text = values;

            this.$refs.amendment_request.isModalOpen = true;
        },
        highlight_deficient_fields: function (deficient_fields) {
            let vm = this;
            for (var deficient_field of deficient_fields) {
                $("#" + "id_" + deficient_field).css("color", 'red');
            }
        },
        deficientFields() {
            let vm = this;
            let deficient_fields = []
            $('.deficiency').each((i, d) => {
                if ($(d).val() != '') {
                    var name = $(d)[0].name
                    var tmp = name.replace("-comment-field", "")
                    deficient_fields.push(tmp);
                    //console.log('data', $("#"+"id_" + tmp))
                }
            });
            //console.log('deficient fields', deficient_fields);
            vm.highlight_deficient_fields(deficient_fields);
        },
        toggleProposal: function (value) {
            this.showingProposal = value
        },
        toggleRequirements: function (value) {
            this.showingRequirements = value
        },
        updateAssignedOfficerSelect: function () {
            console.log('updateAssignedOfficerSelect')
            let vm = this;
            if (vm.proposal.processing_status == 'With Approver') {
                //$(vm.$refs.assigned_officer).val(vm.proposal.assigned_approver);
                //$(vm.$refs.assigned_officer).trigger('change');
                vm.$refs.workflow.updateAssignedOfficerSelect(vm.proposal.assigned_approver)
            }
            else {
                //$(vm.$refs.assigned_officer).val(vm.proposal.assigned_officer);
                //$(vm.$refs.assigned_officer).trigger('change');
                vm.$refs.workflow.updateAssignedOfficerSelect(vm.proposal.assigned_officer)
            }
        },
        assignRequestUser: async function () {
            let vm = this
            console.log('in assignRequestUser')

            fetch(helpers.add_endpoint_json(api_endpoints.proposal, (vm.proposal.id + '/assign_request_user'))).then(async response => {
                if (!response.ok) {
                    return await response.json().then(json => { throw new Error(json); });
                } else {
                    return await response.json();
                }
            })
                .then(data => {
                    vm.proposal = Object.assign({}, data);
                    vm.updateAssignedOfficerSelect();
                })
                .catch(error => {
                    this.updateAssignedOfficerSelect();
                    console.log(error);
                    swal.fire({
                        title: 'Proposal Error',
                        text: error,
                        icon: 'error'
                    })
                })
        },
        /*
        refreshFromResponse:function(response){
            this.proposal = helpers.copyObject(response.body);
            this.$nextTick(() => {
                this.initialiseAssignedOfficerSelect(true);
                this.updateAssignedOfficerSelect();
            });
        },
        */
        assignTo: async function () {
            let vm = this
            console.log('in assignTo')
            let unassign = true;
            let data = {};
            if (this.processing_status == 'With Approver') {
                unassign = this.proposal.assigned_approver != null && this.proposal.assigned_approver != 'undefined' ? false : true;
                data = { 'assessor_id': this.proposal.assigned_approver };
            }
            else {
                unassign = this.proposal.assigned_officer != null && this.proposal.assigned_officer != 'undefined' ? false : true;
                data = { 'assessor_id': this.proposal.assigned_officer };
            }

            let endpoint = 'unassign';
            let payload = {}
            if (!unassign) {
                endpoint = 'assign_to';
                payload = {
                    body: JSON.stringify(data),
                    method: 'POST',
                }
            }

            fetch(helpers.add_endpoint_json(api_endpoints.proposal, (`${vm.proposal.id}/${endpoint}`)),
                payload).then(
                    async response => {
                        if (!response.ok) {
                            return await response.json().then(json => { throw new Error(json); });
                        } else {
                            return await response.json();
                        }
                    })
                .then(data => {
                    vm.proposal = Object.assign({}, data);
                    vm.updateAssignedOfficerSelect();
                })
                .catch(error => {
                    this.updateAssignedOfficerSelect();
                    console.log(error);
                    swal.fire({
                        title: 'Proposal Error',
                        text: error,
                        icon: 'error'
                    })
                })
        },
        switchStatus: async function (new_status) {
            let data = { 'status': new_status, 'approver_comment': this.approver_comment };

            fetch(helpers.add_endpoint_json(api_endpoints.proposal,
                (this.proposal.id + '/switch_status')),
                {
                    body: JSON.stringify(data),
                    method: 'POST',
                }).then(async response => {
                    if (!response.ok) {
                        return await response.json().then(json => { throw new Error(json); });
                    } else {
                        return await response.json();
                    }
                })
                .then(data => {
                    this.proposal = Object.assign({}, data);
                    this.approver_comment = '';
                    this.$nextTick(() => {
                        this.initialiseAssignedOfficerSelect(true);
                        this.updateAssignedOfficerSelect();
                    });
                    //if approver is pushing back proposal to Assessor then navigate the approver back to dashboard page
                    if (this.proposal.processing_status_id == constants.PROPOSAL_STATUS.WITH_APPROVER.ID &&
                        (new_status == 'with_assessor_requirements' || // FIXME What is this processing status for?
                            new_status == constants.PROPOSAL_STATUS.WITH_ASSESSOR)) {
                        this.$router.push({ path: '/internal' });
                    }
                })
                .catch(error => {
                    swal.fire({
                        title: 'Proposal Error',
                        text: error,
                        icon: 'error'
                    });
                });
        },
        initialiseAssignedOfficerSelect: function (reinit = false) {
            console.log('initialiseAssignedOfficerSelect')
            let vm = this;
            if (reinit) {
                $(vm.$refs.assigned_officer).data('select2') ? $(vm.$refs.assigned_officer).select2('destroy') : '';
            }
            // Assigned officer select
            /*
            console.log('Elem: ')
            console.log(vm.$refs.assigned_officer)
            */
            $(vm.$refs.assigned_officer).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder: "Select Officer"
            }).
                on("select2:select", function (e) {
                    var selected = $(e.currentTarget);
                    if (vm.proposal.processing_status == 'With Approver') {
                        vm.proposal.assigned_approver = selected.val();
                    }
                    else {
                        vm.proposal.assigned_officer = selected.val();
                    }
                    vm.assignTo();
                }).on("select2:unselecting", function (e) {
                    var self = $(this);
                    setTimeout(() => {
                        self.select2('close');
                    }, 0);
                }).on("select2:unselect", function (e) {
                    var selected = $(e.currentTarget);
                    if (vm.proposal.processing_status == 'With Approver') {
                        vm.proposal.assigned_approver = null;
                    }
                    else {
                        vm.proposal.assigned_officer = null;
                    }
                    vm.assignTo();
                });
        },
        initialiseSelects: function () {
            let vm = this;
            if (!vm.initialisedSelects) {
                /*
                $(vm.$refs.department_users).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    //placeholder:"Select Referral"
                }).
                on("select2:select",function (e) {
                    var selected = $(e.currentTarget);
                    //vm.selected_referral = selected.val();
                }).
                on("select2:unselect",function (e) {
                    var selected = $(e.currentTarget);
                    //vm.selected_referral = ''
                });
                */
                vm.initialiseAssignedOfficerSelect();
                vm.initialisedSelects = true;
            }
        },
        fetchAdditionalDocumentTypesDict: async function () {
            const response = await fetch('/api/additional_document_types_dict')
            const resData = await response.json()
            this.applySelect2ToAdditionalDocumentTypes(resData)
        },
        revisionToDisplay: async function (revision) {
            console.log("Displaying", revision);
            let vm = this;
            let payload = {
                "revision_id": revision.revision_id,
                "debug": this.debug
            }

            await fetch(helpers.add_endpoint_json(api_endpoints.proposal, vm.proposal.id + '/revision_version'),
                { body: JSON.stringify(payload), method: 'POST' }).then(async response => {
                    if (!response.ok) {
                        return await response.json().then(json => { throw new Error(json); });
                    } else {
                        return response.json();
                    }
                }).then(response => {
                    console.log(response.reference);
                    this.proposal = Object.assign({}, response);
                    this.current_revision_id = revision.revision_id;
                    this.uuid++;
                }).catch(error => {
                    console.error(error);
                });
        },
        fetchProposal: async function () {
            let vm = this;
            fetch(`/api/proposal/${this.$route.params.proposal_id}/`).then(async response => {
                if (!response.ok) {
                    const text = await response.json();
                    throw new Error(text);
                } else {
                    return await response.json();
                }
            })
                .then(data => {
                    vm.proposal = Object.assign({}, data);
                    // Dict of the latest revision's parameters
                    vm.latest_revision = Object.assign({}, data.lodgement_versions[0]);
                    // Set current reivsion id to the latest one on creation
                    vm.current_revision_id = vm.latest_revision.revision_id
                    vm.hasAmendmentRequest = this.proposal.hasAmendmentRequest;
                    if (vm.debug == true) {
                        this.showingProposal = true;
                    }
                })
                .catch(error => {
                    console.log(error);
                })
        },
    },
    mounted: function () {
        let vm = this
        this.$nextTick(() => {
            vm.addEventListeners()
        })
    },
    updated: function () {
        let vm = this;
        if (!vm.panelClickersInitialised) {
            $('.panelClicker[data-toggle="collapse"]').on('click', function () {
                var chev = $(this).children()[0];
                window.setTimeout(function () {
                    $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
                }, 100);
            });
            vm.panelClickersInitialised = true;
        }
        this.$nextTick(() => {
            vm.initialiseOrgContactTable();
            vm.initialiseSelects();
            vm.form = document.forms.new_proposal;
            if (vm.hasAmendmentRequest) {
                vm.deficientFields();
            }
        });
    },
    created: function () {
        this.fetchProposal();
    },
}
</script>
<style scoped>
.horizontal_rule {
    margin: 15px 0 10px 0;
    border-top: 2px solid #888;
}

.assessment_title {
    margin: 20px 0 10px 0;
    border-bottom: 1px solid #888;
    font-weight: bold;
    font-size: 1.3em;
}

.btn-primary {
    margin: 2px;
}
</style>
