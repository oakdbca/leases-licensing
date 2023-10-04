<template lang="html">
    <!-- External Proposal view -->
    <div class="container">
        <div
            v-if="approval"
            class="row justify-content-center align-items-center g-2"
        >
            <div class="col-md-12">
                <h3>
                    Transfer License:
                    {{ approval.lodgement_number }} -
                    {{ approval.approval_type }}
                </h3>
                <ul id="pills-tab" class="nav nav-pills" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button
                            id="holder-tab"
                            class="nav-link active"
                            data-bs-toggle="tab"
                            data-bs-target="#holder"
                            type="button"
                            role="tab"
                            aria-controls="holder"
                            aria-selected="true"
                            @click="holderTabClicked"
                        >
                            <span class="fw-bold">Step 1:</span> Provide
                            Approval Holder Details
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button
                            id="transferee-tab"
                            class="nav-link"
                            data-bs-toggle="tab"
                            data-bs-target="#transferee"
                            type="button"
                            role="tab"
                            aria-controls="transferee"
                            aria-selected="false"
                            @click="transfereeTabClicked"
                        >
                            <span class="fw-bold">Step 2:</span> Select
                            Transferee
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button
                            id="details-tab"
                            class="nav-link"
                            data-bs-toggle="tab"
                            data-bs-target="#details"
                            type="button"
                            role="tab"
                            aria-controls="details"
                            aria-selected="false"
                        >
                            <span class="fw-bold">Step 3:</span> Provide
                            Supporting Documents
                        </button>
                    </li>
                </ul>

                <div class="tab-content">
                    <div
                        v-if="approval.holder_obj"
                        id="holder"
                        class="tab-pane show fade active"
                        role="tabpanel"
                        aria-labelledby="holder-tab"
                    >
                        <Applicant
                            v-if="'individual' == approval.applicant_type"
                            id="licenseHolder"
                            ref="license_holder"
                            :proposal-id="approval.current_proposal"
                            :readonly="readonly"
                            :collapse-form-sections="false"
                        />
                        <OrganisationApplicant
                            v-else
                            ref="license_holder"
                            :org="approval.holder_obj"
                        />
                    </div>
                    <div
                        id="transferee"
                        class="tab-pane show fade"
                        role="tabpanel"
                        aria-labelledby="transferee-tab"
                    >
                        <FormSection
                            :form-collapse="false"
                            label="Transferee"
                            index="fs-details-invoice"
                        >
                            <div class="container">
                                <form>
                                    <div class="mb-3 row">
                                        <label
                                            for="inputName"
                                            class="col-3 col-form-label"
                                            >Select the type of
                                            transferee:</label
                                        >
                                        <div class="col-5">
                                            <ul class="list-group">
                                                <li class="list-group-item">
                                                    <div class="form-check">
                                                        <input
                                                            id=""
                                                            v-model="
                                                                approval
                                                                    .active_transfer
                                                                    .transferee_type
                                                            "
                                                            class="form-check-input"
                                                            type="radio"
                                                            name="transferee_type"
                                                            value="organisation"
                                                            @change="
                                                                transfereeTypeChanged
                                                            "
                                                        />
                                                        <label
                                                            class="form-check-label"
                                                            for=""
                                                        >
                                                            Organisation
                                                        </label>
                                                    </div>
                                                </li>
                                                <li class="list-group-item">
                                                    <div class="form-check">
                                                        <input
                                                            id=""
                                                            v-model="
                                                                approval
                                                                    .active_transfer
                                                                    .transferee_type
                                                            "
                                                            class="form-check-input"
                                                            type="radio"
                                                            name="transferee_type"
                                                            value="individual"
                                                            @change="
                                                                transfereeTypeChanged
                                                            "
                                                        />
                                                        <label
                                                            class="form-check-label"
                                                            for=""
                                                        >
                                                            Individual
                                                        </label>
                                                    </div>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                    <div
                                        v-if="
                                            approval.active_transfer
                                                .transferee_type ==
                                            'organisation'
                                        "
                                        class="row mb-3"
                                    >
                                        <div class="col-3">
                                            Organisation Name or ABN
                                        </div>
                                        <div class="col-5">
                                            <input
                                                id="inputName"
                                                ref="search"
                                                type="text"
                                                class="form-control"
                                                placeholder="Start typing the name or ABN"
                                            />
                                        </div>
                                    </div>
                                    <div
                                        v-if="
                                            approval.active_transfer
                                                .transferee_type == 'individual'
                                        "
                                        class="row mb-3"
                                    >
                                        <div class="col-3">Name or Email</div>
                                        <div class="col-5">
                                            <input
                                                id="inputName"
                                                ref="search"
                                                type="text"
                                                class="form-control"
                                                placeholder="Start typing the person's name or email"
                                            />
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </FormSection>
                    </div>
                    <div
                        id="details"
                        class="tab-pane show fade"
                        role="tabpanel"
                        aria-labelledby="details-tab"
                    >
                        <FormSection
                            :form-collapse="false"
                            label="Lease or Licence to be Transferred"
                            index="lease-license-to-be-transferred"
                        >
                            <div class="container">
                                <div class="row mb-3">
                                    <div class="col-3 fw-bold">
                                        Lodgement Number
                                    </div>
                                    <div class="col-5">
                                        {{ approval.lodgement_number }}
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-3 fw-bold">
                                        Approval Document
                                    </div>
                                    <div class="col-5">
                                        <i
                                            class="fa-solid fa-file-pdf fa-lg ps-1 text-danger"
                                        ></i
                                        >&nbsp;
                                        <a
                                            target="_blank"
                                            :href="approval.licence_document"
                                            >Approval.pdf</a
                                        >
                                    </div>
                                </div>
                            </div>
                        </FormSection>
                        <FormSection
                            :form-collapse="false"
                            label="Supporting Documents"
                            index="supporting-documents"
                        >
                            <div class="container">
                                <div class="row mb-3">
                                    <div class="col-3 fw-bold">
                                        Attach any Supporting Documents
                                    </div>
                                    <div class="col-5">
                                        <FileField
                                            id="supporting_documents"
                                            ref="supporting_documents"
                                            name="supporting_documents"
                                            :is-repeatable="true"
                                            :document-action-url="
                                                supportingDocumentsUrl
                                            "
                                            :replace_button_by_text="true"
                                        />
                                    </div>
                                </div>
                            </div>
                        </FormSection>
                    </div>
                </div>
            </div>
        </div>
        <div class="navbar fixed-bottom bg-navbar me-1">
            <div class="container">
                <div class="col-12 text-end">
                    <button
                        type="button"
                        class="btn btn-secondary me-2"
                        @click=""
                    >
                        Cancel
                    </button>
                    <button
                        type="button"
                        class="btn btn-primary me-2"
                        @click=""
                    >
                        Save and Continue
                    </button>
                    <button
                        type="button"
                        class="btn btn-primary me-2"
                        @click=""
                    >
                        Save and Exit
                    </button>
                    <button type="button" class="btn btn-primary" @click="">
                        Initiate Transfer
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers, utils } from '@/utils/hooks';
import { v4 as uuid } from 'uuid';

import FormSection from '@/components/forms/section_toggle.vue';
import Applicant from '@/components/common/applicant.vue';
import OrganisationApplicant from '@/components/common/organisation_applicant.vue';
import FileField from '@/components/forms/filefield_immediate.vue';

export default {
    name: 'ApprovalTransfer',
    components: {
        FormSection,
        Applicant,
        FileField,
        OrganisationApplicant,
    },
    props: {
        approvalId: {
            type: Number,
            default: null,
        },
    },
    data() {
        return {
            approval: null,
        };
    },
    computed: {
        supportingDocumentsUrl: function () {
            return helpers.add_endpoint_join(
                api_endpoints.approval_transfers,
                this.approval.active_transfer.id +
                    '/process_supporting_document/'
            );
        },
    },
    created() {
        this.fetchApproval();
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
                    vm.approval_details_id = uuid();
                    console.log('External approval data: ', vm.approval);
                })
                .catch((error) => {
                    console.log(
                        `Error fetching external approval data ${error}`
                    );
                });
        },
        holderTabClicked: function () {
            let vm = this;
            let organisation_contacts =
                vm.$refs.license_holder.$refs.organisation_contacts ?? null;
            if (organisation_contacts) {
                try {
                    organisation_contacts.$refs.organisation_contacts_datatable.vmDataTable.draw(
                        'page'
                    );
                } catch (error) {
                    console.log(
                        'Error refreshing organisation contacts datatable'
                    );
                }
            }
        },
        transfereeTabClicked: function () {
            setTimeout(() => {
                this.$refs.search.focus();
            }, 200);
        },
        transfereeTypeChanged: function () {
            this.$refs.search.focus();
        },
    },
};
</script>

<style lang="scss" scoped></style>
