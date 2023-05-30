<template lang="html">
    <div id="proposedIssuanceApproval">
        <div class="container-fluid">
            <form class="form-horizontal" name="approvalForm">
                <div class="row">
                    <VueAlert :show.sync="showError" type="danger"><strong v-html="errorString"></strong></VueAlert>
                    <div class="col-sm-12" v-if="registrationOfInterest">
                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label class="control-label pull-left" for="Name">{{ decisionLabel }}</label>
                            </div>
                            <div v-for="(text, key) in approvalDecisionText" :key="key">
                                <div class="form-check col-sm-12">
                                    <input type="radio" class="form-check-input" :name="key" :id="key" :value="key"
                                        v-model="selectedDecision" :disabled="readonly" />
                                    <label class="form-check-label" :for="key" style="font-weight:normal">{{ text
                                    }}</label>
                                </div>
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label v-if="withApprover || readonly" class="control-label pull-left"
                                    for="Name">Details</label>
                                <label v-else class="control-label pull-left" for="Name">Proposed Details</label>
                            </div>
                            <div class="col-sm-9">
                                <RichText :proposalData="proposedDecisionDetails" ref="registration_of_interest_details"
                                    id="registration_of_interest_details" :can_view_richtext_src=true
                                    :key="proposedApprovalKey" v-model="proposedDecisionDetails" :readonly="readonly" />
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label v-if="withApprover || readonly" class="control-label pull-left" for="Name">BCC
                                    email</label>
                                <label v-else class="control-label pull-left" for="Name">Proposed BCC email</label>
                            </div>
                            <div class="col-sm-9">
                                <input type="text" class="form-control" name="approval_bcc" style="width:70%;"
                                    ref="bcc_email" v-model="approval.bcc_email" :readonly="readonly">
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-sm-12">
                                <label v-if="submitter_email && applicant_email" class="control-label pull-left"
                                    for="Name">After approving this proposal, approval will be emailed to
                                    {{ submitter_email }} and {{ applicant_email }}.</label>
                                <label v-else class="control-label pull-left" for="Name">After approving this proposal,
                                    approval will be emailed to {{ submitter_email }}.</label>
                            </div>
                        </div>
                    </div>
                    <div class="col-sm-12" v-if="leaseLicence">
                        <div class="form-group">
                            <div class="row mb-3">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left" for="approvalType">Approval Type</label>
                                </div>
                                <div class="col-sm-9">
                                    <select :disabled="readonly" ref="select_approvaltype" class="form-control"
                                        v-model="selectedApprovalTypeId">
                                        <option></option>
                                        <option v-for="atype in approvalTypes" :value="atype.id" :key="atype.name">
                                            {{ atype.name }}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <div class="col-sm-3">
                                    <label v-if="withApprover" class="control-label pull-left"
                                        for="Name">Commencement</label>
                                    <label v-else class="control-label pull-left" for="Name">Commencement</label>
                                </div>
                                <div class="col-sm-9">
                                    <div class="input-group date" ref="start_date">
                                        <input :disabled="readonly" type="date" class="form-control" name="start_date"
                                            placeholder="DD/MM/YYYY" v-model="approval.start_date">
                                    </div>
                                </div>
                            </div>
                            <div class="row" v-show="showstartDateError">
                                <VueAlert class="col-sm-12" type="danger"><strong>{{ startDateErrorString }}</strong>
                                </VueAlert>
                            </div>
                            <div class="row mb-3">
                                <div class="col-sm-3">
                                    <label v-if="withApprover || readonly" class="control-label pull-left"
                                        for="Name">Expiry</label>
                                    <label v-else class="control-label pull-left" for="Name">Expiry</label>
                                </div>
                                <div class="col-sm-9">
                                    <div class="input-group date" ref="due_date">
                                        <input :disabled="readonly" type="date" class="form-control" name="due_date"
                                            placeholder="DD/MM/YYYY" v-model="approval.expiry_date">
                                    </div>
                                </div>
                            </div>
                            <div class="row" v-show="showtoDateError">
                                <VueAlert class="col-sm-12" type="danger"><strong>{{ toDateErrorString }}</strong>
                                </VueAlert>
                            </div>
                            <div class="row mb-3">
                                <div class="col-sm-3">
                                    <label v-if="withApprover" class="control-label pull-left" for="Name">Details</label>
                                    <label v-else class="control-label pull-left" for="Name">Details</label>
                                </div>
                                <div class="col-sm-9">
                                    <RichText :proposalData="approval.details" ref="lease_licence_details"
                                        id="lease_licence_details" :can_view_richtext_src=true
                                        :key="selectedApprovalTypeName"
                                        :placeholder_text="selectedApprovalTypeDetailsPlaceholder"
                                        v-model="approval.details" :readonly="readonly" />
                                </div>
                            </div>
                            <div class="row mb-3">
                                <div class="col-sm-3">
                                    <label for="supporting_documents">File</label>
                                </div>
                                <div class="col-sm-9">
                                    <FileField ref="proposed_approval_documents" name="proposed_approval_documents"
                                        id="proposed_approval_documents" :isRepeatable="true"
                                        :documentActionUrl="proposedApprovalDocumentsUrl" :replace_button_by_text="true"
                                        :readonly="readonly" />
                                </div>
                            </div>
                            <div class="row mb-3">
                                <div class="col-sm-3">
                                    <label v-if="withApprover || readonly" class="control-label pull-left" for="Name">CC
                                        email</label>
                                    <label v-else class="control-label pull-left" for="Name">Proposed CC email</label>
                                </div>
                                <div class="col-sm-9">
                                    <input type="text" class="form-control" name="approval_cc" ref="cc_email"
                                        v-model="approval.cc_email" :disabled="readonly">
                                </div>
                            </div>
                        </div>
                        <div class="form-group"
                            v-if="leaseLicence && !withApprover && !proposalIsApproved || alwaysShowDocuments">
                            <hr>
                            <ProposedApprovalDocuments v-if="proposal" ref="proposed_issuance_documents"
                                :proposal="proposal" :proposal_id="proposal.id"
                                :processing_status="proposal.processing_status" :approvalTypes="approvalTypes"
                                :selectedApprovalTypeId="selectedApprovalTypeId" :key="selectedApprovalTypeId"
                                :readonly=false />
                        </div>
                        <div>
                            <div class="row mb-3">
                                <div class="col-sm-4">
                                    <label class="control-label pull-left" for="recordManagementNumber">Record Management
                                        Number</label>
                                </div>
                                <div class="col-sm-8">
                                    <input class="form-control" v-model="approval.record_management_number" type="text"
                                        required>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </div>
        <p v-if="can_preview">Click <a href="#" @click.prevent="preview">here</a> to preview the approval letter.</p>

        <div slot="footer">
        </div>
    </div>
</template>

<script>
import { constants } from '@/utils/hooks'
import VueAlert from '@vue-utils/alert.vue'
import RichText from '@/components/forms/richtext.vue'
import {
    api_endpoints,
    helpers,
    utils
}
    from '@/utils/hooks'
import FileField from '@/components/forms/filefield_immediate.vue'
import ProposedApprovalDocuments from '@/components/internal/proposals/proposed_approval_documents.vue'
import Swal from 'sweetalert2'

export default {
    name: 'ProposedApprovalForm',
    components: {
        VueAlert,
        RichText,
        FileField,
        ProposedApprovalDocuments,
    },
    props: {
        proposal_id: {
            type: Number,
            required: true
        },
        processing_status: {
            type: String,
            required: true
        },
        proposal_type: {
            type: String,
            required: true
        },
        proposalIsApproved: {
            type: Boolean,
            required: false
        },
        readonly: {
            type: Boolean,
            default: false
        },
        submitter_email: {
            type: String,
            required: true
        },
        applicant_email: {
            type: String,
        },
        proposedApprovalKey: {
            type: String,
        },
        proposedApprovalState: {
            type: String,
        },
        proposal: {
            type: Object,
            required: true,
        },
        decisionLabel: {
            type: String,
            default: 'Decision',
        },
        alwaysShowDocuments: {
            type: Boolean,
            default: false,
        },
    },
    data: function () {
        return {
            selectedDecision: null,
            isModalOpen: false,
            form: null,
            approval: {},
            approvalTypes: [],
            selectedApprovalType: {},
            selectedApprovalTypeId: null,
            // Document Types arrays rely on selectedApprovalTypeId
            //state: 'proposed_approval',
            issuingApproval: false,
            approvalDecisionText: {
                "approve_lease_licence": "Invite applicant to apply for a lease or licence",
                "approve_competitive_process": "Start Competitive process",
                "decline_application": "Decline Application"
            },
            validation_form: null,
            errors: false,
            toDateError: false,
            startDateError: false,
            errorString: '',
            toDateErrorString: '',
            startDateErrorString: '',
            successString: '',
            success: false,
            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true
            },
            warningString: 'Please attach Level of Approval document before issuing Approval',
            uuid: 0,
        }
    },
    computed: {
        selectedApprovalTypeExists: function () {
            if (this.selectedApprovalType && this.selectedApprovalType.id) {
                return true;
            }
        },
        leaseLicenceApprovalDocumentsUrl: function () {
            return helpers.add_endpoint_join(
                api_endpoints.proposal,
                this.proposal.id + '/process_lease_licence_approval_document/'
            )
        },
        proposedApprovalDocumentsUrl: function () {
            return helpers.add_endpoint_join(
                api_endpoints.proposal,
                this.proposal.id + '/process_proposed_approval_document/'
            )
        },
        selectedApprovalDocumentTypes: function () {
            if (this.selectedApprovalType) {
                return this.selectedApprovalType.approval_type_document_types;
            }
        },
        selectedApprovalTypeName: function () {
            if (this.selectedApprovalType) {
                return this.selectedApprovalType.name
            }
        },
        selectedApprovalTypeDetailsPlaceholder: function () {
            if (this.selectedApprovalType) {
                return this.selectedApprovalType.details_placeholder
            }
        },
        proposedDecisionDetails: function () {
            /** Returns proposed decision details depending on whether the proposed decision
             *  by the assessor is an approval or a decline.
             */

            if (this.approval.decision) {
                return this.approval.details;
            }
            else if (this.proposal.proposed_decline_status) {
                return this.proposal.proposaldeclineddetails.reason;
            } else {
                return "";
            }
        },
        showError: function () {
            var vm = this;
            return vm.errors;
        },
        showtoDateError: function () {
            var vm = this;
            return vm.toDateError;
        },
        showstartDateError: function () {
            var vm = this;
            return vm.startDateError;
        },
        title: function () {
            return this.processing_status == 'With Approver' ? 'Issue Approval' : `Propose to Approve Application: ${this.proposal.lodgement_number}`;
        },
        is_amendment: function () {
            return this.proposal_type == 'Amendment' ? true : false;
        },
        csrf_token: function () {
            return helpers.getCookie('csrftoken')
        },
        withApprover: function () {
            return this.proposal.processing_status_id == constants.PROPOSAL_STATUS.WITH_APPROVER.ID ? true : false;
        },
        isApproved: function () {

        },
        can_preview: function () {
            return this.processing_status == 'With Approver' ? true : false;
        },
        preview_licence_url: function () {
            return (this.proposal_id) ? `/preview/licence-pdf/${this.proposal_id}` : '';
        },
        registrationOfInterest: function () {
            if (this.proposal && this.proposal.application_type.name === 'registration_of_interest') {
                return true;
            }
        },
        leaseLicence: function () {
            if (this.proposal && this.proposal.application_type.name === 'lease_licence') {
                return true;
            }
        },
    },
    methods: {
        handleApprovalTypeChangeEvent(id) {
            this.updateSelectedApprovalType(id);
            this.initSelectDocument();
        },
        updateSelectedApprovalType(id) {
            // clear existing doc arrays
            if (this.approval) {
                this.approval.selected_document_types = [];
            }
            if (this.proposal.proposed_issuance_approval) {
                this.proposal.proposed_issuance_approval.selected_document_types = [];
            }

            this.selectedApprovalTypeId = id;
        },
        preview: function () {
            let vm = this;
            let formData = new FormData(vm.form)
            // convert formData to json
            let jsonObject = {};
            for (const [key, value] of formData.entries()) {
                jsonObject[key] = value;
            }
            vm.post_and_redirect(vm.preview_licence_url, { 'csrfmiddlewaretoken': vm.csrf_token, 'formData': JSON.stringify(jsonObject) });
        },
        post_and_redirect: function (url, postData) {
            /* http.post and ajax do not allow redirect from Django View (post method),
               this function allows redirect by mimicking a form submit.
               usage:  vm.post_and_redirect(vm.application_fee_url, {'csrfmiddlewaretoken' : vm.csrf_token});
            */
            var postFormStr = "<form method='POST' target='_blank' name='Preview Licence' action='" + url + "'>";
            for (var key in postData) {
                if (postData.hasOwnProperty(key)) {
                    postFormStr += "<input type='hidden' name='" + key + "' value='" + postData[key] + "'>";
                }
            }
            postFormStr += "</form>";
            var formElement = $(postFormStr);
            $('body').append(formElement);
            $(formElement).submit();
        },
        ok: async function () {
            await this.sendData();
        },
        cancel: function () {
            this.close()
        },
        close: function () {
            this.isModalOpen = false;
            this.approval = {};
            this.errors = false;
        },
        fetchContact: async function (id) {
            const response = await fetch(api_endpoints.contact(id));
            this.contact = await response.json();
            this.isModalOpen = true;
        },
        sendData: async function () {
            this.errors = false;
            this.issuingApproval = true;
            this.approval.assessment = this.assessment;

            this.$nextTick(async () => {
                if (this.registrationOfInterest) {
                    this.approval.details = this.$refs.registration_of_interest_details.detailsText;
                    this.approval.decision = this.selectedDecision;
                } else if (this.leaseLicence) {
                    this.approval.details = this.$refs.lease_licence_details.detailsText;
                    this.approval.approval_type = this.selectedApprovalTypeId;
                    this.approval.selected_document_types = this.$refs.proposed_issuance_documents.selectedDocumentTypes;
                }
                if (this.proposedApprovalState == 'proposed_approval') {
                    const response = await fetch(helpers.add_endpoint_json(api_endpoints.proposals, this.proposal_id + '/proposed_approval'), {
                        body: JSON.stringify(this.approval),
                        method: 'POST',
                    })
                    if (response.ok) {
                        this.issuingApproval = false;
                        Swal.fire({
                            title: `Proposal to Approve: ${this.proposal.lodgement_number}`,
                            text: 'Submitted successfully.',
                            icon: 'success',
                            confirmButtonText: 'OK'
                        })
                        this.close();
                        this.$router.push({ path: '/internal' }); //Navigate to dashboard page after Propose issue.
                    } else {
                        this.errors = true;
                        this.issuingApproval = false;
                        this.errorString = await helpers.parseFetchError(response)
                    }
                } else if (this.proposedApprovalState == 'final_approval') {
                    const response = await fetch(helpers.add_endpoint_json(api_endpoints.proposals, this.proposal_id + '/final_approval'), {
                        body: JSON.stringify(this.approval),
                        method: 'POST',
                    })
                    if (response.ok) {
                        this.issuingApproval = false;
                        this.close();
                        this.$router.push({ path: '/internal' }); //Navigate to dashboard page after Propose issue.
                    } else {
                        this.errors = true;
                        this.issuingApproval = false;
                        this.errorString = await helpers.parseFetchError(response)
                    }
                }
            });
        },
        initSelectDocument: function () {
            let vm = this;
            vm.$refs.proposed_issuance_documents.initSelectDocument();
        },
        /**
         * Initialise the select2 control for selecting the approval type of the application
         */
        initSelectApprovalType: function () {
            let vm = this;

            $(vm.$refs.select_approvaltype).select2({
                "theme": "bootstrap-5",
                allowClear: true,
                placeholder: "Select an approval type",
            }).on("select2:select", function (e) {
                var selected = $(e.currentTarget);
                vm.handleApprovalTypeChangeEvent(Number(selected.val()));
            }).on("select2:unselecting", function (e) {
                var self = $(this);
                setTimeout(() => {
                    self.select2('close');
                }, 0);
            }).on("select2:unselect", function (e) {
                let unselected_id = e.params.data.id;
            });
        },
    },
    created: async function () {
        let vm = this;
        vm.form = document.forms.approvalForm;
        this.approval = Object.assign({}, this.proposal.proposed_issuance_approval);

        let initialisers = [
            utils.fetchApprovalTypes(),
        ]
        Promise.all(initialisers).then(data => {
            for (let approvalType of data[0]) {
                vm.approvalTypes.push(approvalType)
            }

            // Approval Type
            if (vm.approval.approval_type) {
                vm.selectedApprovalTypeId = vm.approval.approval_type;
            }

            this.selectedApprovalTypeId = this.approval.approval_type;

        });

        this.$nextTick(() => {
            if (this.approval.decision) {
                this.selectedDecision = this.approval.decision;
            } else if (this.proposal.proposed_decline_status) {
                this.selectedDecision = "decline_application";
            }

            this.initSelectApprovalType();
        });
    },
}
</script>
