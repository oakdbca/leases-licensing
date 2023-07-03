<template lang="html">
    <!-- External Proposal view -->
    <div class="container">
        <div class="row justify-content-center align-items-center g-2">
            <div class="col-md-12">
                <h3>License: {{ approval.lodgement_number }}</h3>
                <!-- Nav tabs -->
                <ul class="nav nav-pills" id="pills-tab" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button
                            class="nav-link"
                            id="applicant-tab"
                            data-bs-toggle="tab"
                            data-bs-target="#applicant"
                            type="button"
                            role="tab"
                            aria-controls="applicant"
                            aria-selected="true"
                        >
                            Holder
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button
                            class="nav-link active"
                            id="details-tab"
                            data-bs-toggle="tab"
                            data-bs-target="#details"
                            type="button"
                            role="tab"
                            aria-controls="details"
                            aria-selected="false"
                        >
                            Details
                        </button>
                    </li>
                    <!-- <li class="nav-item" role="presentation">
                        <button
                            class="nav-link"
                            id="transfer-tab"
                            data-bs-toggle="tab"
                            data-bs-target="#transfer"
                            type="button"
                            role="tab"
                            aria-controls="transfer"
                            aria-selected="false"
                        >
                            Transfer
                        </button>
                    </li> -->
                </ul>

                <!-- Tab panes -->
                <div class="tab-content">
                    <div
                        class="tab-pane show fade"
                        id="applicant"
                        role="tabpanel"
                        aria-labelledby="applicant-tab"
                    >
                        <Applicant
                            v-if="'individual' == approval.applicant_type"
                            :email_user="approval.holder_obj"
                            id="licenseHolder"
                            :readonly="readonly"
                            :collapseFormSections="false"
                            :proposalId="approval.id"
                        />
                        <OrganisationApplicant
                            v-else
                            :org="approval.holder_obj"
                        />
                    </div>
                    <div
                        class="tab-pane show fade active"
                        id="details"
                        role="tabpanel"
                        aria-labelledby="details-tab"
                    >

                        <ApprovalDetails
                            :approval_details="approval"
                        />

                        <FormSection
                            :formCollapse="false"
                            label="Invoices"
                            Index="fs-details-invoice"
                        >
                            <InvoicesTable
                                ref="invoice_table"
                                :approval_id="approval.id"
                                level="external"
                            />
                        </FormSection>
                    </div>
                    <!-- <div
                        class="tab-pane show fade"
                        id="transfer"
                        role="tabpanel"
                        aria-labelledby="transfer-tab"
                    >
                        transfer
                    </div> -->
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers, utils } from '@/utils/hooks'

import FormSection from '@/components/forms/section_toggle.vue'
import Applicant from '@/components/common/applicant.vue'
import OrganisationApplicant from '@/components/common/organisation_applicant.vue'
import InvoicesTable from '@/components/common/table_invoices.vue'
import ApprovalDetails from '@/components/common/approval_details.vue'

export default {
    name: 'ExternalApprovalDetail',
    data() {
        let vm = this
        vm._uid = vm._.uid // Vue3
        return {
            approval: {
                holder_obj: {},
                approval_type_obj: {},
            },
        }
    },
    components: {
        FormSection,
        Applicant,
        OrganisationApplicant,
        InvoicesTable,
        ApprovalDetails,
    },
    props: {
        approvalId: {
            type: Number,
        },
        readonly: {
            type: Boolean,
            default: false,
        },
    },
    methods: {
        fetchApproval: function () {
            let vm = this
            let url = helpers.add_endpoint_json(
                api_endpoints.approvals,
                vm.$route.params.approval_id
            )
            utils
                .fetchUrl(url)
                .then((data) => {
                    vm.approval = Object.assign({}, data)
                    console.log('External approval data: ', vm.approval)
                })
                .catch((error) => {
                    console.log(
                        `Error fetching external approval data ${error}`
                    )
                })
        },
    },
    created: async function () {
        let vm = this
        vm.fetchApproval()
    },
}
</script>
