<template id="proposal_approval">
    <div>
        <div v-if="displayApprovedMsg" class="col-md-12 alert alert-success">
            <!--p>The {{ applicationTypeNameDisplay }} was approved to proceed to a full application on date by {{ proposal.assigned_approver.email }}</p-->
            <p>The {{ applicationTypeNameDisplay }} was approved to proceed to a {{ fullApplicationText }} on {{ approvalIssueDate }} by { insert approver name here }</p>
            <!--p>Expiry date: {{ approvalExpiryDate }}</p>
            <p>Permit: <a target="_blank" :href="proposal.permit">approval.pdf</a></p-->
        </div>
        <div v-if="displayDeclinedMsg" class="col-md-12 alert alert-warning">
            <p>The proposal was declined. The decision was emailed to {{ proposal.submitter.email }}</p>
        </div>

        <!--div class="card card-default">
            <div class="card-header">
                <h3 v-if="!isFinalised" class="card-title">Proposed Decision
                    <a class="panelClicker" :href="'#'+proposedDecision" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="proposedDecision">
                        <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                    </a>
                </h3>
                <h3 v-else class="card-title">Decision
                    <a class="panelClicker" :href="'#'+proposedDecision" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="proposedDecision">
                        <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                    </a>
                </h3>
            </div>
            <div class="card-body" :id="proposedDecision">
                <div class="row">
                    <div class="col-sm-12">
                        <template v-if="!proposal.proposed_decline_status">
                            <template v-if="isFinalised">
                                <p><strong>Decision: Issue</strong></p>
                                <p><strong>Start date: {{proposal.proposed_issuance_approval.start_date}}</strong></p>
                                <p><strong>Expiry date: {{proposal.proposed_issuance_approval.expiry_date}}</strong></p>
                                <p><strong>CC emails: {{proposal.proposed_issuance_approval.cc_email}}</strong></p>
                            </template>
                            <template v-else>
                                <p><strong>Proposed decision: Issue</strong></p>
                                <p><strong>Proposed cc emails: {{proposal.proposed_issuance_approval.cc_email}}</strong></p>
                            </template>
                        </template>
                        <template v-else>
                            <strong v-if="!isFinalised">Proposed decision: Decline</strong>
                            <strong v-else>Decision: Decline</strong>
                        </template>
                    </div>
                </div>
            </div>
        </div-->
        <FormSection :formCollapse="false" label="Decision" Index="proposal_decision">
            <ProposedIssuanceForm
                v-if="proposal"
                :proposal="proposal"
                ref="proposed_approval_form"
                :processing_status="proposal.processing_status"
                :proposal_id="proposal.id"
                :proposal_type='proposal.proposal_type.code'
                :submitter_email="proposal.submitter.email"
                :applicant_email="proposal.applicant"
                :key="proposedApprovalKey"
                :proposedApprovalKey="proposedApprovalKey"
                :proposedApprovalState="proposedApprovalState"
                :readonly=true
            />
        </FormSection>

        <FormSection :formCollapse="false" label="Documents" Index="proposal_documents">
            <!-- TODO -->
        </FormSection>

        <FormSection v-if="show_invoicing_details" :formCollapse="false" label="Invoicing Details" Index="proposal_invoicing_details">
            <InvoicingDetails
                :invoicing_details="proposal.invoicing_details"
            />
        </FormSection>
    </div>
</template>
<script>
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks'
import { constants } from '@/utils/hooks'
import ProposedIssuanceForm from '@/components/internal/proposals/proposed_issuance_form.vue'
import FormSection from "@/components/forms/section_toggle.vue"
import InvoicingDetails from "@/components/common/invoicing_details.vue"

export default {
    name: 'InternalProposalApproval',
    props: {
        proposal: Object,
        proposedApprovalState: "",
        proposedApprovalKey: null
    },
    data: function() {
        let vm = this;
        return {
            proposedDecision: "proposal-decision-"+vm._.uid,
            proposedLevel: "proposal-level-"+vm._.uid,
            uploadedFile: null,
            component_site_selection_key: '',
        }
    },
    watch:{
    },
    components:{
        ProposedIssuanceForm,
        FormSection,
        InvoicingDetails,
    },
    computed:{
        debug: function(){
            if (this.$route.query.debug){
                return this.$route.query.debug === 'true'
            }
            return false
        },
        display_approval_screen: function(){
            if (this.debug)
                return true
            let ret_val =
                this.proposal.processing_status_id == constants.PROPOSAL_STATUS.WITH_APPROVER.ID ||
                this.proposal.processing_status_id == constants.PROPOSAL_STATUS.APPROVED_EDITING_INVOICING.ID ||
                this.isFinalised
            return ret_val
        },
        display_requirements: function(){
            let ret_val =
                this.proposal.processing_status_id == constants.PROPOSAL_STATUS.WITH_ASSESSOR_CONDITIONS.ID ||
                ((this.proposal.processing_status_id == constants.PROPOSAL_STATUS.WITH_APPROVER.ID || this.isFinalised) && this.showingRequirements)
            return ret_val
        },
        /*
        showElectoralRoll: function(){
            // TODO: implement
            return true
        },
        */
        showElectoralRoll: function() {
            let show = false;
            if (this.proposal && ['wla', 'mla'].includes(this.proposal.application_type_code)) {
                show = true;
            }
            return show;
        },
        readonly: function() {
            return true
        },
        contactsURL: function(){
            return this.proposal!= null ? helpers.add_endpoint_json(api_endpoints.organisations, this.proposal.applicant.id + '/contacts') : '';
        },
        isLoading: function() {
          return this.loading.length > 0
        },
        csrf_token: function() {
          return helpers.getCookie('csrftoken')
        },
        isFinalised: function(){
            return this.proposal.processing_status_id === constants.PROPOSAL_STATUS.DECLINED.ID || this.proposal.processing_status_id === constants.PROPOSAL_STATUS.APPROVED.ID;
        },
        canAssess: function(){
            return true  // TODO: Implement correctly.  May not be needed though

            //return this.proposal && this.proposal.assessor_mode.assessor_can_assess ? true : false;
        },
        hasAssessorMode:function(){
            return this.proposal && this.proposal.assessor_mode.has_assessor_mode ? true : false;
        },
        canAction: function(){

            return true  // TODO: implement this.  This is just temporary solution

            //if (this.proposal.processing_status == 'With Approver'){
            //    return this.proposal && (this.proposal.processing_status == 'With Approver' || this.proposal.processing_status == 'With Assessor' || this.proposal.processing_status == 'With Assessor (Requirements)') && !this.isFinalised && !this.proposal.can_user_edit && (this.proposal.current_assessor.id == this.proposal.assigned_approver || this.proposal.assigned_approver == null ) && this.proposal.assessor_mode.assessor_can_assess? true : false;
            //}
            //else{
            //    return this.proposal && (this.proposal.processing_status == 'With Approver' || this.proposal.processing_status == 'With Assessor' || this.proposal.processing_status == 'With Assessor (Requirements)') && !this.isFinalised && !this.proposal.can_user_edit && (this.proposal.current_assessor.id == this.proposal.assigned_officer || this.proposal.assigned_officer == null ) && this.proposal.assessor_mode.assessor_can_assess? true : false;
            //}
        },
        //canLimitedAction: function(){

        //    //return false  // TODO: implement this.  This is just temporary solution

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
        //},
        canSeeSubmission: function(){
            return this.proposal && (this.proposal.processing_status != 'With Assessor (Requirements)' && this.proposal.processing_status != 'With Approver' && !this.isFinalised)
        },
        isApprovalLevelDocument: function(){
            return this.proposal && this.proposal.processing_status == 'With Approver' && this.proposal.approval_level != null && this.proposal.approval_level_document == null ? true : false;
        },
        approvalIssueDate: function() {
            if (this.proposal) {
                return this.proposal.approval_issue_date;
            }
        },
        fullApplicationText: function() {
            if (this.proposal.proposed_issuance_approval.decision === 'approve_lease_licence') {
                return 'full application';
            } else if (this.proposal.proposed_issuance_approval.decision === 'approve_competitive_process') {
                return 'Competitive Process';
            }
        },
        show_invoicing_details: function() {
            if (this.debug)
                return true

            let display = false
            if (this.proposal && 
                this.proposal.application_type && 
                this.proposal.application_type.name === constants.APPLICATION_TYPES.LEASE_LICENCE && 
                this.proposal.processing_status_id === constants.PROPOSAL_STATUS.APPROVED_EDITING_INVOICING.ID &&
                this.proposal.accessing_user_roles.includes(constants.ROLES.FINANCE.ID))
                    display = true
            return display
        },
        applicationTypeNameDisplay: function() {
            if (this.proposal) {
                return this.proposal.application_type.name_display;
            }
        },
        displayAwaitingPaymentMsg: function(){
            let display = false
            console.log(this.proposal.processing_status)
            if (this.proposal.processing_status_id === constants.PROPOSAL_STATUS.AWAITING_PAYMENT.ID){
                display = true
            }
            return display
        },
        displayApprovedMsg: function(){
            let display = false
            if (this.proposal.processing_status_id === constants.PROPOSAL_STATUS.APPROVED.ID){
                display = true
            }
            return display
        },
        displayDeclinedMsg: function(){
            let display = false
            if (this.proposal.processing_status_id === constants.PROPOSAL_STATUS.DECLINED.ID){
                display = true
            }
            return display
        },
        approvalExpiryDate: function() {
            let returnDate = null;
            if (this.proposal && this.proposal.end_date) {
                returnDate = moment(this.proposal.end_date, 'YYYY-MM-DD').format('DD/MM/YYYY');
            }
            return returnDate;
        },
        hasAssessorMode(){
            return this.proposal.assessor_mode.has_assessor_mode;
        },
        isFinalised: function(){
            return this.proposal.processing_status == 'Approved' || this.proposal.processing_status == 'Declined';
        },
        isApprovalLevel:function(){
            return this.proposal.approval_level != null ? true : false;
        },

    },
    methods:{
        readFile: function() {
            let vm = this;
            let _file = null;
            var input = $(vm.$refs.uploadedFile)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]);
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            vm.uploadedFile = _file;
            vm.save()
        },
        removeFile: function(){
            let vm = this;
            vm.uploadedFile = null;
            vm.save()
        },
        save: function(){
            let vm = this;
                let data = new FormData(vm.form);
                data.append('approval_level_document', vm.uploadedFile)
                if (vm.proposal.approval_level_document) {
                    data.append('approval_level_document_name', vm.proposal.approval_level_document[0])
                }
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/approval_level_document'),data,{
                emulateJSON:true
            }).then(res=>{
                vm.proposal = res.body;
                vm.$emit('refreshFromResponse',res);

                },err=>{
                swal(
                    'Submit Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });


        },
        uploadedFileName: function() {
            return this.uploadedFile != null ? this.uploadedFile.name: '';
        },
        addRequirement(){
            this.$refs.requirement_detail.isModalOpen = true;
        },
        removeRequirement(_id){
            let vm = this;
            swal({
                title: "Remove Requirement",
                text: "Are you sure you want to remove this requirement?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Remove Requirement',
                confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.delete(helpers.add_endpoint_json(api_endpoints.proposal_requirements,_id))
                .then((response) => {
                    vm.$refs.requirements_datatable.vmDataTable.ajax.reload();
                }, (error) => {
                    console.log(error);
                });
            },(error) => {
            });
        },
    },
    mounted: function(){
        let vm = this;
    }
}
</script>
<style scoped>
</style>
