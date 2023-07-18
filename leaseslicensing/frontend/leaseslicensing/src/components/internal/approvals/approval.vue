<template>
    <div v-if="approval" id="internalApproval" class="container">
        <div class="row">
            <h3>
                {{ approvalLabel }}: {{ approval.lodgement_number }}
                <small
                    v-if="approval.original_leaselicense_number"
                    class="text-muted"
                >
                    (Migrated from:
                    {{ approval.original_leaselicense_number }})</small
                >
            </h3>
            <div class="col-md-3">
                <CommsLogs
                    :comms_url="comms_url"
                    :logs_url="logs_url"
                    :comms_add_url="comms_add_url"
                    :disable_add_entry="false"
                />

                <div class="row mt-2 mb-2">
                    <div class="col">
                        <div class="card card-default">
                            <div class="card-header">Submission</div>
                            <div class="card-body card-collapse">
                                <div class="row">
                                    <div class="col-sm-12 top-buffer-s">
                                        <strong>Issued on</strong><br />
                                        {{ formatDate(approval.issue_date) }}
                                    </div>
                                    <div class="col-sm-12 top-buffer-s">
                                        <table class="table small-table">
                                            <tr>
                                                <th>Lodgement</th>
                                                <th>Date</th>
                                                <th>Action</th>
                                            </tr>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <StatusPanel :status="approval.status" />

                <div
                    v-if="
                        'Current (Pending Renewal Review)' == approval.status &&
                        approval.can_renew
                    "
                    class="row mt-2 mb-2"
                >
                    <div class="col">
                        <div class="card card-default">
                            <div class="card-header">Review Renewal</div>
                            <div class="card-body card-collapse">
                                <div class="mb-2">
                                    <button
                                        class="btn btn-primary btn-licensing"
                                        @click="renewalRevew(true)"
                                    >
                                        Allow Renewal
                                    </button>
                                </div>
                                <div>
                                    <button
                                        class="btn btn-danger btn-licensing"
                                        @click="renewalRevew(false)"
                                    >
                                        Disallow Renewal
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-if="showEditingInvoicingOptions" class="row mt-2 mb-2">
                    <div class="col">
                        <div class="card card-default">
                            <div class="card-header">
                                Edit Invoicing Details
                            </div>
                            <div class="card-body card-collapse">
                                <div class="mb-2">
                                    <button
                                        class="btn btn-primary btn-licensing"
                                        @click="completeEditingInvoicing(true)"
                                    >
                                        Complete Editing
                                    </button>
                                </div>
                                <div>
                                    <button
                                        class="btn btn-secondary btn-licensing"
                                        @click="cancelEditingInvoicing(false)"
                                    >
                                        Cancel Editing
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-9">
                <ul id="pills-tab" class="nav nav-pills" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button
                            id="pills-holder-tab"
                            class="nav-link active"
                            data-bs-toggle="pill"
                            data-bs-target="#pills-holder"
                            role="tab"
                            aria-controls="pills-holder"
                            aria-selected="true"
                        >
                            Applicant
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button
                            id="pills-details-tab"
                            class="nav-link"
                            data-bs-toggle="pill"
                            data-bs-target="#pills-details"
                            role="tab"
                            aria-controls="pills-details"
                            aria-selected="true"
                        >
                            Details
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button
                            id="pills-map-tab"
                            class="nav-link"
                            data-bs-toggle="pill"
                            data-bs-target="#pills-map"
                            role="tab"
                            aria-controls="pills-map"
                            aria-selected="true"
                        >
                            Map
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button
                            id="pills-invoicing-tab"
                            class="nav-link"
                            data-bs-toggle="pill"
                            data-bs-target="#pills-invoicing"
                            role="tab"
                            aria-controls="pills-invoicing"
                            aria-selected="true"
                            @click="tabClicked('invoicing')"
                        >
                            Invoicing
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button
                            id="pills-related-items-tab"
                            class="nav-link"
                            data-bs-toggle="pill"
                            data-bs-target="#pills-related-items"
                            role="tab"
                            aria-controls="pills-related-items"
                            aria-selected="true"
                        >
                            Related Items
                        </button>
                    </li>
                </ul>

                <div id="pills-tabContent" class="tab-content">
                    <div
                        id="pills-holder"
                        class="tab-pane fade show active"
                        role="tabpanel"
                        aria-labelledby="pills-holder-tab"
                    >
                        <Applicant
                            v-if="'individual' == approval.applicant_type"
                            id="approvalHolder"
                            :email_user="approval.holder_obj"
                            :readonly="true"
                            :collapse-form-sections="false"
                        />
                        <OrganisationApplicant
                            v-else
                            :org="approval.holder_obj"
                        />
                    </div>

                    <div
                        id="pills-details"
                        class="tab-pane fade"
                        role="tabpanel"
                    >
                        <FormSection
                            :form-collapse="false"
                            label="License"
                            index="oBody"
                        >
                            <div
                                v-if="loading.length == 0"
                                :id="oBody"
                                class="card-body"
                            >
                                <form
                                    class="form-horizontal"
                                    action="index.html"
                                    method="post"
                                >
                                    <div class="row mb-3">
                                        <label
                                            for="lodgement_number"
                                            class="col-sm-4 col-form-label"
                                            >Lodgement Number</label
                                        >
                                        <div class="col-sm-8">
                                            <input
                                                class="form-control"
                                                type="text"
                                                :value="
                                                    approval.lodgement_number
                                                "
                                                readonly
                                            />
                                        </div>
                                    </div>
                                    <div
                                        v-if="
                                            approval.original_leaselicense_number
                                        "
                                        class="row mb-3"
                                    >
                                        <label
                                            for="lodgement_number"
                                            class="col-sm-4 col-form-label"
                                            >Migrated from</label
                                        >
                                        <div class="col-sm-8">
                                            <input
                                                class="form-control"
                                                type="text"
                                                :value="
                                                    approval.original_leaselicense_number
                                                "
                                                readonly
                                            />
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label
                                            for="lodgement_number"
                                            class="col-sm-4 col-form-label"
                                            >Approval Type</label
                                        >
                                        <div class="col-sm-8">
                                            <input
                                                class="form-control"
                                                type="text"
                                                :value="
                                                    approval.application_type
                                                "
                                                readonly
                                            />
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label
                                            for="start_date"
                                            class="col-sm-4 col-form-label"
                                            >Commencement</label
                                        >
                                        <div class="col-sm-8">
                                            <input
                                                id="issue_date"
                                                class="form-control"
                                                type="text"
                                                :value="
                                                    formatDate(
                                                        approval.start_date
                                                    )
                                                "
                                                readonly
                                            />
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label
                                            for="expiry_date"
                                            class="col-sm-4 col-form-label"
                                            >Expiry</label
                                        >
                                        <div class="col-sm-8">
                                            <input
                                                id="issue_date"
                                                class="form-control"
                                                type="text"
                                                :value="
                                                    formatDate(
                                                        approval.expiry_date
                                                    )
                                                "
                                                readonly
                                            />
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label
                                            for="record_management_number"
                                            class="col-sm-4 col-form-label"
                                            >Record Management Number</label
                                        >
                                        <div class="col-sm-8">
                                            <input
                                                id="record_management_number"
                                                class="form-control"
                                                type="text"
                                                :value="
                                                    approval.record_management_number
                                                "
                                                readonly
                                            />
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label
                                            for=""
                                            class="col-sm-4 col-form-label"
                                            >{{ approvalLabel }}</label
                                        >
                                        <div class="col-sm-4">
                                            <p>
                                                <a
                                                    target="_blank"
                                                    :href="
                                                        approval.licence_document
                                                    "
                                                    class="form-label pull-left"
                                                    >Licence.pdf</a
                                                >
                                            </p>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </FormSection>
                    </div>

                    <div id="pills-map" class="tab-pane fade" role="tabpanel">
                        Map
                    </div>

                    <div
                        id="pills-invoicing"
                        class="tab-pane fade"
                        role="tabpanel"
                        aria-labelledby="pills-invoicing-tab"
                    >
                        <InvoicesTable
                            v-if="loadInvoices"
                            ref="invoice_table"
                            :approval-id="approval.id"
                            level="internal"
                        />
                        <FormSection
                            v-if="loadInvoices && showEditingInvoicingOptions"
                            class="mt-5"
                            :form-collapse="false"
                            label="Edit Invoicing Details"
                            index="invoicing_details"
                        >
                            <InvoicingDetails
                                :invoicing-details="
                                    approval.current_proposal.invoicing_details
                                "
                                @updateInvoicingDetails="updateInvoicingDetails"
                            />
                        </FormSection>
                    </div>

                    <div
                        id="pills-related-items"
                        class="tab-pane fade"
                        role="tabpanel"
                        aria-labelledby="pills-related-items-tab"
                    >
                        <FormSection
                            :form-collapse="false"
                            label="Related Items"
                            index="related_items"
                        >
                            <TableRelatedItems
                                :ajax_url="related_items_ajax_url"
                            />
                        </FormSection>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
/*globals bootstrap, moment */
import CommsLogs from '@common-utils/comms_logs.vue'
import Applicant from '@/components/common/applicant.vue'
import OrganisationApplicant from '@/components/common/organisation_applicant.vue'
import InvoicesTable from '@/components/common/table_invoices.vue'
import FormSection from '@/components/forms/section_toggle.vue'
import { api_endpoints, constants, helpers } from '@/utils/hooks'
import Swal from 'sweetalert2'
import TableRelatedItems from '@/components/common/table_related_items.vue'
import InvoicingDetails from '@/components/common/invoicing_details.vue'

export default {
    name: 'ApprovalDetail',
    components: {
        CommsLogs,
        FormSection,
        Applicant,
        OrganisationApplicant,
        InvoicesTable,
        TableRelatedItems,
        InvoicingDetails,
    },
    data() {
        let vm = this
        vm._uid = vm._.uid // Vue3
        return {
            showExpired: false,
            moorings_datatable_id: 'moorings-datatable-' + vm._uid,
            ml_vessels_datatable_id: 'ml-vessels-datatable-' + vm._uid,
            ml_authorised_users_datatable_id:
                'ml-authorised-users-datatable-' + vm._uid,
            loading: [],
            approval: null,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            adBody: 'adBody' + vm._uid,
            pBody: 'pBody' + vm._uid,
            cBody: 'cBody' + vm._uid,
            oBody: 'oBody' + vm._uid,
            org: {
                address: {},
            },
            loadInvoices: false,
            // Filters
            logs_url: helpers.add_endpoint_json(
                api_endpoints.approvals,
                vm.$route.params.approval_id + '/action_log'
            ),
            comms_url: helpers.add_endpoint_json(
                api_endpoints.approvals,
                vm.$route.params.approval_id + '/comms_log'
            ),
            comms_add_url: helpers.add_endpoint_json(
                api_endpoints.approvals,
                vm.$route.params.approval_id + '/add_comms_log'
            ),

            related_items_ajax_url: helpers.add_endpoint_join(
                api_endpoints.approvals,
                vm.$route.params.approval_id + '/related_items'
            ),
        }
    },
    computed: {
        debug: function () {
            return Object.hasOwnProperty.call(this.$route.query, 'debug') &&
                this.$route.query.debug === 'true'
                ? true
                : false
        },
        isLoading: function () {
            return this.loading.length > 0
        },
        approvalLabel: function () {
            let description = ''
            if (this.approval && this.approval.approval_type_dict) {
                description = this.approval.approval_type_dict.description
            } else {
                description = 'License'
            }
            return description
        },
        showEditingInvoicingOptions: function () {
            return (
                this.approval &&
                constants.APPROVAL_STATUS.CURRENT_EDITING_INVOICING.TEXT ==
                    this.approval.status
            )
        },
    },
    created: async function () {
        const response = await fetch(
            helpers.add_endpoint_json(
                api_endpoints.approvals,
                this.$route.params.approval_id
            )
        )
        const resData = await response.json()
        this.approval = Object.assign({}, resData)
        this.approval.applicant_id = resData.applicant_id
        if (this.approval.submitter.postal_address == null) {
            this.approval.submitter.postal_address = {}
        }
        this.$nextTick(function () {
            if (window.location.hash == '#edit-invoicing') {
                console.log(this.approval)
                console.log('opening invoicing tab')
                this.loadInvoices = true
                let tab_element = document.querySelector('#pills-invoicing-tab')
                let tab = new bootstrap.Tab(tab_element)
                tab.show()
                window.scrollTo(0, document.body.scrollHeight)
            }
        })
    },
    mounted: function () {},
    methods: {
        tabClicked: function (param) {
            if (param == 'invoicing') {
                console.log('invoicing tab clicked')
                this.loadInvoices = true
            }
        },
        formatDate: function (data) {
            return data ? moment(data).format(this.DATE_TIME_FORMAT) : ''
        },
        renewalRevew: function (canBeRenewed) {
            let vm = this
            Swal.fire({
                title: 'Are you sure?',
                text:
                    'You are about to ' +
                    (canBeRenewed ? 'allow' : 'disallow') +
                    ' renewal of approval ' +
                    vm.approval.lodgement_number +
                    '.',
                icon: 'warning',
                reverseButtons: true,
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                confirmButtonText:
                    (canBeRenewed ? 'Allow' : 'Disallow') + ' Renewal',
            }).then((result) => {
                if (result.isConfirmed) {
                    let vm = this
                    const requestOptions = {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ can_be_renewed: canBeRenewed }),
                    }
                    fetch(
                        helpers.add_endpoint_json(
                            api_endpoints.approvals,
                            vm.approval.id + '/review_renewal'
                        ),
                        requestOptions
                    ).then(
                        async (response) => {
                            const data = await response.json()
                            if (!response.ok) {
                                const error =
                                    (data && data.message) ||
                                    response.statusText
                                console.log(error)
                                return Promise.reject(error)
                            }
                            let successMessage =
                                'The approval status has been reset to Current and will expire without being renewed.'
                            if (canBeRenewed) {
                                successMessage =
                                    'The approval holder has been notified that they may renew the approval.'
                            }
                            Swal.fire(
                                'Renewal Review Complete',
                                successMessage,
                                'success'
                            )
                            vm.approval = Object.assign({}, data)
                        },
                        (error) => {
                            console.log(error)
                        }
                    )
                }
            })
        },
        updateInvoicingDetails: function (value) {
            this.approval.current_proposal.invoicing_details = value
        },
        completeEditingInvoicing: function () {
            alert('Call api to modify invoices based on new invoicing details')
        },
        cancelEditingInvoicing: function () {
            let vm = this
            Swal.fire({
                title: 'Cancel Editing Invoicing Details',
                text: 'Are you sure you want to cancel editing invoicing details (any unsaved changes will be lost)?',
                icon: 'warning',
                showCancelButton: true,
                reverseButtons: true,
                confirmButtonText: 'Cancel Editing',
                cancelButtonText: 'Continue Editing',
                confirmButtonColor: '#226fbb',
                buttonsStyling: false,
                customClass: {
                    confirmButton: 'btn btn-primary',
                    cancelButton: 'btn btn-secondary me-2',
                },
            }).then(async (result) => {
                if (result.isConfirmed) {
                    let requestOptions = {
                        method: 'PATCH',
                    }
                    fetch(
                        helpers.add_endpoint_join(
                            api_endpoints.approvals,
                            vm.approval.id + '/cancel_editing_invoicing/'
                        ),
                        requestOptions
                    ).then(
                        async (response) => {
                            const data = await response.json()
                            if (!response.ok) {
                                const error =
                                    (data && data.message) ||
                                    response.statusText
                                console.log(error)
                                Promise.reject(error)
                            }
                            vm.$router.push({
                                name: 'internal-approvals-dash',
                            })
                        },
                        (error) => {
                            console.log(error)
                        }
                    )
                }
            })
        },
    },
}
</script>
