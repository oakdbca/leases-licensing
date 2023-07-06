<template lang="html">
    <!-- External Proposal view -->
    <div class="container">
        <div class="row justify-content-center align-items-center g-2">
            <div class="col-md-12">
                <h3>License: {{ approval.lodgement_number }}</h3>
                <!-- Nav tabs -->
                <ul id="pills-tab" class="nav nav-pills" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button
                            id="applicant-tab"
                            class="nav-link"
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
                            id="details-tab"
                            class="nav-link active"
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
                </ul>

                <!-- Tab panes -->
                <div class="tab-content">
                    <div
                        id="applicant"
                        class="tab-pane show fade"
                        role="tabpanel"
                        aria-labelledby="applicant-tab"
                    >
                        <Applicant
                            v-if="'individual' == approval.applicant_type"
                            id="licenseHolder"
                            :email_user="approval.holder_obj"
                            :readonly="readonly"
                            :collapse-form-sections="false"
                            :proposal-id="approval.id"
                        />
                        <OrganisationApplicant
                            v-else
                            :org="approval.holder_obj"
                        />
                    </div>
                    <div
                        id="details"
                        class="tab-pane show fade active"
                        role="tabpanel"
                        aria-labelledby="details-tab"
                    >
                        <ApprovalDetails :approval-details="approval" />

                        <FormSection
                            :form-collapse="false"
                            label="Invoices"
                            index="fs-details-invoice"
                        >
                            <InvoicesTable
                                ref="invoice_table"
                                :approval_id="approval.id"
                                level="external"
                            />
                        </FormSection>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers, utils } from '@/utils/hooks';

import FormSection from '@/components/forms/section_toggle.vue';
import Applicant from '@/components/common/applicant.vue';
import OrganisationApplicant from '@/components/common/organisation_applicant.vue';
import InvoicesTable from '@/components/common/table_invoices.vue';
import ApprovalDetails from '@/components/common/approval_details.vue';

export default {
    name: 'ExternalApprovalDetail',
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
            default: null,
        },
        readonly: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        let vm = this;
        vm._uid = vm._.uid; // Vue3
        return {
            approval: {
                holder_obj: {},
                approval_type_obj: {},
            },
        };
    },
    created: async function () {
        let vm = this;
        vm.fetchApproval();
    },
    methods: {
        fetchApproval: function () {
            let vm = this;
            let url = helpers.add_endpoint_json(
                api_endpoints.approvals,
                vm.$route.params.approval_id
            );
            utils
                .fetchUrl(url)
                .then((data) => {
                    vm.approval = Object.assign({}, data);
                    console.log('External approval data: ', vm.approval);
                })
                .catch((error) => {
                    console.log(
                        `Error fetching external approval data ${error}`
                    );
                });
        },
    },
};
</script>
