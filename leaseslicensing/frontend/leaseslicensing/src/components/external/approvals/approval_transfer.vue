<template lang="html">
    <!-- External Proposal view -->
    <div class="container">
        <div
            v-if="approval"
            class="row justify-content-center align-items-center g-2"
        >
            <div class="col-md-12">
                <h3>
                    {{ approval.approval_type__type }} Transfer:
                    {{ approval.lodgement_number }} -
                    {{ approval.approval_type }}
                </h3>
                <!-- {{ approval.active_transfer }} -->
                <div v-if="errors" class="container">
                    <BootstrapAlert
                        v-if="errors"
                        id="errors"
                        ref="errors"
                        class="d-flex align-items-center"
                        type="danger"
                        icon="exclamation-triangle-fill"
                    >
                        <ErrorRenderer :errors="errors" />
                    </BootstrapAlert>
                </div>
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
                            <span class="fw-bold">Step 1:</span> Provide Holder
                            Details
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
                            :approval-transfer-applicant="
                                approval.active_transfer.applicant
                            "
                            :readonly="false"
                            :collapse-form-sections="false"
                            @update-approval-transfer-applicant="
                                updateApprovalTransferApplicant
                            "
                            @save-approval-transfer-applicant="
                                saveApprovalTransferApplicant
                            "
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
                                            Select Organisation
                                        </div>
                                        <div class="col-5">
                                            <select
                                                id="search"
                                                ref="search"
                                                class="form-select"
                                                placeholder="Start typing the Organisation's Name or ABN"
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
                                        <div class="col-3">
                                            Select Individual
                                        </div>
                                        <div class="col-5">
                                            <select
                                                id="search"
                                                ref="search"
                                                class="form-select"
                                                placeholder="Start typing the individual's name or email"
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
                            v-if="selectedTransferee"
                            :form-collapse="false"
                            label="Parties"
                            index="original-holder-and-transferee"
                        >
                            <div class="container">
                                <span class="fw-bold me-2"
                                    >Lease/Licence Holder</span
                                >
                                <span class="badge bg-primary p-2 fw-bold me-2">
                                    {{ approval.holder }}
                                </span>
                                <span class="fw-bold me-2"
                                    >transferring to
                                    <i
                                        class="fa fa-long-arrow-right text-success"
                                        aria-hidden="true"
                                    ></i
                                ></span>
                                <span class="badge bg-primary fw-bold p-2 me-2">
                                    {{ selectedTransferee }}
                                </span>
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
        <BootstrapSpinner v-if="loading" class="text-primary" />
        <div class="navbar fixed-bottom bg-navbar me-1">
            <div class="container">
                <div class="col-12 text-end">
                    <button
                        type="button"
                        class="btn btn-secondary me-2"
                        @click="cancelApprovalTransfer"
                    >
                        Cancel
                    </button>
                    <button
                        type="button"
                        class="btn btn-primary me-2"
                        @click="saveAndContinue"
                    >
                        Save and Continue
                    </button>
                    <button
                        type="button"
                        class="btn btn-primary me-2"
                        @click="saveAndExit"
                    >
                        Save and Exit
                    </button>
                    <button
                        type="button"
                        class="btn btn-primary"
                        @click="initiateTransfer"
                    >
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
import Applicant from '@/components/common/approval_transfer_applicant.vue';
import OrganisationApplicant from '@/components/common/organisation_applicant.vue';
import FileField from '@/components/forms/filefield_immediate.vue';
import ErrorRenderer from '@common-utils/ErrorRenderer.vue';

export default {
    name: 'ApprovalTransfer',
    components: {
        ErrorRenderer,
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
            loading: false,
            approval: null,
            searchApiEndpoint: api_endpoints.organisation_lookup,
            searchPlaceholder: 'Start typing the Organisation Name or ABN',
            selectedTransferee: null,
            errors: null,
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
    mounted() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    methods: {
        fetchApproval: function () {
            this.loading = true;
            let vm = this;
            let url = helpers.add_endpoint_json(
                api_endpoints.approvals,
                vm.$route.params.approval_id
            );
            utils
                .fetchUrl(url)
                .then((data) => {
                    vm.approval = Object.assign({}, data);
                    if (
                        vm.approval.active_transfer.processing_status != 'draft'
                    ) {
                        vm.$router.push({
                            name: 'external-dashboard',
                        });
                    }
                    vm.approval_details_id = uuid();
                    vm.$nextTick(() => {
                        vm.setPlaceholderAndApiEndpoint();
                    });
                })
                .catch((error) => {
                    console.log(
                        `Error fetching external approval data ${error}`
                    );
                })
                .finally(() => {
                    vm.loading = false;
                });
        },
        updateApprovalTransferApplicant: function (applicant) {
            this.approval.active_transfer.applicant = applicant;
        },
        saveApprovalTransferApplicant: function (applicant) {
            this.approval.active_transfer.applicant = applicant;
            this.saveAndContinue();
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
                this.initialiseSearch();
                if (this.approval.active_transfer.transferee) {
                    let option = new Option(
                        this.approval.active_transfer.transferee_name,
                        this.approval.active_transfer.transferee,
                        true,
                        true
                    );
                    $('#search')
                        .append(option)
                        .trigger('change')
                        .trigger({
                            type: 'select2:select',
                            params: {
                                data: {
                                    id: this.approval.active_transfer
                                        .transferee,
                                    text: this.approval.active_transfer
                                        .transferee_name,
                                },
                            },
                        });
                    this.selectedTransferee =
                        this.approval.active_transfer.transferee_name;
                } else {
                    $('#search').select2('open');
                }
            }, 200);
        },
        setPlaceholderAndApiEndpoint: function () {
            if (this.approval.active_transfer.transferee_type == 'individual') {
                this.searchPlaceholder =
                    "Start typing the Individual's Name or Email";
                this.searchApiEndpoint = api_endpoints.person_lookup;
                this.initialiseSearch();
            } else {
                this.searchPlaceholder =
                    'Start typing the Organisation Name or ABN';
                this.searchApiEndpoint = api_endpoints.organisation_lookup;
                this.initialiseSearch();
            }
        },
        transfereeTypeChanged: function () {
            this.setPlaceholderAndApiEndpoint();
            setTimeout(() => {
                this.initialiseSearch();
                $('#search').select2('open');
                this.resetTransferee();
            }, 200);
        },
        initialiseSearch: function () {
            let vm = this;
            $('#search')
                .select2({
                    minimumInputLength: 2,
                    theme: 'bootstrap-5',
                    allowClear: true,
                    placeholder: vm.searchPlaceholder,
                    ajax: {
                        url: vm.searchApiEndpoint,
                        dataType: 'json',
                        data: function (params) {
                            console.log(params);
                            let query = {
                                term: params.term,
                                type: 'public',
                            };
                            return query;
                        },
                        processResults: function (data, params) {
                            if (data.results.length == 0) {
                                swal.fire({
                                    title: 'No Results Found',
                                    text: `No results found for the search term '${params.term}'. The transferee must have a valid account in the leases and licensing system.`,
                                    icon: 'warning',
                                    confirmButtonText: 'OK',
                                });
                            }
                            return {
                                results: data.results,
                            };
                        },
                    },
                })
                .on('select2:open', function () {
                    const searchField = $(
                        `[aria-controls='select2-search-results']`
                    );
                    searchField[0].focus();
                })
                .on('select2:select', function (e) {
                    vm.approval.active_transfer.transferee = e.params.data.id;
                    vm.approval.active_transfer.transferee_name =
                        e.params.data.text;
                    document.activeElement.blur();
                    vm.selectedTransferee = e.params.data.text;
                })
                .on('select2:clear', function () {
                    vm.resetTransferee();
                });
        },
        resetTransferee: function () {
            this.approval.active_transfer.transferee = null;
            this.approval.active_transfer.transferee_name = '';
        },
        cancelApprovalTransfer: function () {
            this.loading = true;
            swal.fire({
                title: 'Confirm Cancellation of Transfer',
                text: `Are you sure you want to cancel the transfer of ${this.approval.lodgement_number} - ${this.approval.approval_type}?`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Yes, Cancel Transfer',
                cancelButtonText: 'No, Keep Transfer',
                reverseButtons: true,
            })
                .then((result) => {
                    if (result.isConfirmed) {
                        fetch(
                            helpers.add_endpoint_join(
                                api_endpoints.approval_transfers,
                                this.approval.active_transfer.id
                            ) + 'cancel/',
                            {
                                method: 'PATCH',
                            }
                        )
                            .then((response) => {
                                if (response.ok) {
                                    swal.fire({
                                        title: 'Success',
                                        text: `Applicant to transfer ${this.approval.lodgement_number} - ${this.approval.approval_type} Cancelled`,
                                        icon: 'success',
                                        confirmButtonText: 'OK',
                                    });
                                    this.$router.push({
                                        name: 'external-dashboard',
                                    });
                                }
                            })
                            .catch((error) => {
                                console.log(
                                    `Error cancelling approval transfer ${error}`
                                );
                            });
                    }
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        saveAndContinue: async function () {
            this.loading = true;
            this.errors = null;
            this.approval.active_transfer.applicant_for_writing =
                this.approval.active_transfer.applicant;
            fetch(
                helpers.add_endpoint_join(
                    api_endpoints.approval_transfers,
                    this.approval.active_transfer.id
                ),
                {
                    method: 'PUT',
                    body: JSON.stringify(this.approval.active_transfer),
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            )
                .then(async (response) => {
                    if (response.ok) {
                        swal.fire({
                            title: 'Success',
                            text: 'Transfer Application Saved',
                            icon: 'success',
                            confirmButtonText: 'OK',
                        });
                    } else {
                        const responseJSON = await response.json();
                        this.errors = responseJSON.errors;
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                        console.error(this.errors);
                    }
                })
                .catch((error) => {
                    console.log(`Error saving approval transfer ${error}`);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        saveAndExit: function () {
            this.saveAndContinue();
            this.$router.push({
                name: 'external-dashboard',
            });
        },
        initiateTransfer: function () {
            this.loading = true;
            this.errors = null;
            this.approval.active_transfer.applicant_for_writing =
                this.approval.active_transfer.applicant;
            fetch(
                helpers.add_endpoint_join(
                    api_endpoints.approval_transfers,
                    this.approval.active_transfer.id
                ) + 'initiate/',
                {
                    method: 'PATCH',
                    body: JSON.stringify(this.approval.active_transfer),
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            )
                .then(async (response) => {
                    if (response.ok) {
                        swal.fire({
                            title: 'Success',
                            text: `${this.approval.lodgement_number} - ${this.approval.approval_type} Transfer to ${this.selectedTransferee} Initiated`,
                            icon: 'success',
                            confirmButtonText: 'OK',
                        });
                        this.$router.push({
                            name: 'external-approval-transfer-initiated',
                        });
                    } else {
                        const responseJSON = await response.json();
                        this.errors = responseJSON.errors;
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                        console.error(this.errors);
                    }
                })
                .catch((error) => {
                    console.log(`Error saving approval transfer ${error}`);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
    },
};
</script>

<style lang="scss" scoped></style>
