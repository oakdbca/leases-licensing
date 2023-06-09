<template lang="html">
    <div id="proposedIssuanceApproval">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large :scrollable="true">
            <ProposedIssuanceForm v-if="proposal" :proposal="proposal" ref="proposed_approval_form"
                :processing_status="proposal.processing_status" :proposal_id="proposal.id"
                :proposal_type="proposal.proposal_type ? proposal.proposal_type.code : ''"
                :submitter_email="proposal.submitter && proposal.submitter.email ? proposal.submitter.email : ''"
                :applicant_email="applicant_email" :key="proposedApprovalKey" :proposedApprovalKey="proposedApprovalKey"
                :proposedApprovalState="proposedApprovalState" :alwaysShowDocuments="true" />
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue'
import VueAlert from '@vue-utils/alert.vue'
import RichText from '@/components/forms/richtext.vue'
import FileField from '@/components/forms/filefield_immediate.vue'
import ProposedIssuanceForm from '@/components/internal/proposals/proposed_issuance_form.vue'
export default {
    name: 'Proposed-Approval',
    components: {
        modal,
        VueAlert,
        RichText,
        FileField,
        ProposedIssuanceForm,
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
    },
    data: function () {
        return {
            isModalOpen: false,
            title: "",
        }
    },
    watch: {
        isModalOpen: function (newVal, oldVal) {
            if (newVal) {
                this.$nextTick(() => {
                    this.$refs.proposed_approval_form.focus();
                });
            }
        },
    },
    computed: {
        submitter_email: function () {
            if (this.proposal.submitter) {
                return this.proposal.submitter.email
            } else {
                return this.proposal.applicant_obj.email
            }
        },
        applicant_email: function () {
            return this.proposal && this.proposal.applicant.email ? this.proposal.applicant.email : '';
        },
    },
    methods: {
        ok: async function () {
            await this.$refs.proposed_approval_form.validateForm();
        },
        cancel: function () {
            this.close()
        },
        close: function () {
            this.isModalOpen = false;
            this.approval = {};
            this.errors = false;
        },
    },
    mounted: function () {
        this.$nextTick(() => {
            console.log(this.$refs);
            this.title = this.$refs.proposed_approval_form.title;
        });
    },
}
</script>
