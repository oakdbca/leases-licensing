<template>
    <div v-if="approval" class="container" id="internalApproval">
        <div v-if="debug">
            <div>internal/proposals/approval.vue</div>
            <button type="button" class="btn btn-light" @click="debug_createApprovalPDF">create Approval.PDF</button>
        </div>
        <div class="row">
            <h3>{{ approvalLabel }}: {{ approval.lodgement_number }}</h3>
            <div class="col-md-3">
                <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url"
                    :disable_add_entry="false" />

                <div class="row mt-2 mb-2">
                    <div class="col">
                        <div class="card card-default">
                            <div class="card-header">
                                Submission
                            </div>
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

                <div v-if="'Current (Pending Renewal Review)' == approval.status && approval.can_renew"
                    class="row mt-2 mb-2">
                    <div class="col">
                        <div class="card card-default">
                            <div class="card-header">
                                Review Renewal
                            </div>
                            <div class="card-body card-collapse">
                                <div class="mb-2"><button @click="renewalRevew(true)"
                                        class="btn btn-primary licensing-btn">Allow
                                        Renewal</button></div>
                                <div><button @click="renewalRevew(false)" class="btn btn-danger licensing-btn">Disallow
                                        Renewal</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
            <div class="col-md-9">

                <ul class="nav nav-pills" id="pills-tab" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="pills-holder-tab" data-bs-toggle="pill"
                            data-bs-target="#pills-holder" role="tab" aria-controls="pills-holder" aria-selected="true">
                            Applicant
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="pills-details-tab" data-bs-toggle="pill"
                            data-bs-target="#pills-details" role="tab" aria-controls="pills-details" aria-selected="true">
                            Details
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="pills-map-tab" data-bs-toggle="pill" data-bs-target="#pills-map"
                            role="tab" aria-controls="pills-map" aria-selected="true">
                            Map
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="pills-invoicing-tab" data-bs-toggle="pill"
                            data-bs-target="#pills-invoicing" role="tab" aria-controls="pills-invoicing"
                            aria-selected="true">
                            Invoicing
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="pills-related-items-tab" data-bs-toggle="pill"
                            data-bs-target="#pills-related-items" role="tab" aria-controls="pills-related-items"
                            aria-selected="true">
                            Related Items
                        </button>
                    </li>
                </ul>

                <div class="tab-content" id="pills-tabContent">
                    <div class="tab-pane fade show active" id="pills-holder" role="tabpanel"
                        aria-labelledby="pills-holder-tab">
                        <Applicant v-if="'individual' == approval.applicant_type" :email_user="approval.holder_obj"
                            id="approvalHolder" :readonly="true" :collapseFormSections="false" />
                        <OrganisationApplicant v-else :org="approval.holder_obj" />
                    </div>

                    <div class="tab-pane fade" id="pills-details" role="tabpanel">
                        <FormSection :formCollapse="false" label="License" Index="oBody">
                            <div v-if="loading.length == 0" class="card-body" :id="oBody">
                                <form class="form-horizontal" action="index.html" method="post">
                                    <div class="row mb-3">
                                        <label for="lodgement_number" class="col-sm-3 col-form-label">Lodgement
                                            Number</label>
                                        <div class="col-sm-6">
                                            <input class="form-control" type="text" :value="approval.lodgement_number"
                                                readonly />
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label for="lodgement_number" class="col-sm-3 col-form-label">Approval Type</label>
                                        <div class="col-sm-6">
                                            <input class="form-control" type="text" :value="approval.application_type"
                                                readonly />
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label for="start_date" class="col-sm-3 col-form-label">Commencement</label>
                                        <div class="col-sm-6">
                                            <input class="form-control" id="issue_date" type="text"
                                                :value="formatDate(approval.start_date)" readonly />
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label for="expiry_date" class="col-sm-3 col-form-label">Expiry</label>
                                        <div class="col-sm-6">
                                            <input class="form-control" id="issue_date" type="text"
                                                :value="formatDate(approval.expiry_date)" readonly />
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label for="" class="col-sm-3 col-form-label">{{ approvalLabel }}</label>
                                        <div class="col-sm-4">
                                            <p><a target="_blank" :href="approval.licence_document"
                                                    class="form-label pull-left">Licence.pdf</a></p>
                                        </div>
                                    </div>

                                </form>
                            </div>
                        </FormSection>
                    </div>

                    <div class="tab-pane fade" id="pills-map" role="tabpanel">
                        Map
                    </div>

                    <div class="tab-pane fade" id="pills-invoicing" role="tabpanel">
                        Invoicing
                    </div>

                    <div class="tab-pane fade" id="pills-related-items" role="tabpanel">
                        Related Items
                    </div>
                </div>

                <div class="row">



                </div>
            </div>
        </div>
    </div>
</template>
<script>
import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import Applicant from '@/components/common/applicant.vue'
import OrganisationApplicant from '@/components/common/organisation_applicant.vue'
import FormSection from "@/components/forms/section_toggle.vue"
import { api_endpoints, helpers } from '@/utils/hooks'
import Swal from 'sweetalert2'
//import OnSiteInformation from '@/components/common/apiary/section_on_site_information.vue'
//import TemporaryUse from '@/components/common/apiary/section_temporary_use.vue'
//import ComponentSiteSelection from '@/components/common/apiary/component_site_selection.vue'
//import SectionAnnualRentalFee from '@/components/common/apiary/section_annual_rental_fee.vue'
export default {
    name: 'ApprovalDetail',
    data() {
        let vm = this;
        vm._uid = vm._.uid; // Vue3
        return {
            showExpired: false,
            moorings_datatable_id: 'moorings-datatable-' + vm._uid,
            ml_vessels_datatable_id: 'ml-vessels-datatable-' + vm._uid,
            ml_authorised_users_datatable_id: 'ml-authorised-users-datatable-' + vm._uid,
            loading: [],
            approval: null,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            adBody: 'adBody' + vm._uid,
            pBody: 'pBody' + vm._uid,
            cBody: 'cBody' + vm._uid,
            oBody: 'oBody' + vm._uid,
            org: {
                address: {}
            },

            // Filters
            logs_url: helpers.add_endpoint_json(api_endpoints.approvals, vm.$route.params.approval_id + '/action_log'),
            comms_url: helpers.add_endpoint_json(api_endpoints.approvals, vm.$route.params.approval_id + '/comms_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.approvals, vm.$route.params.approval_id + '/add_comms_log'),
            moorings_datatable_headers: [
                //'Id',
                'Mooring',
                'Sticker',
                'Licensee',
                'Allocated By',
                'Mobile',
                'Email',
            ],

            moorings_datatable_options: {
                autoWidth: false,
                responsive: true,
                columns: [
                    {
                        data: "mooring_name",
                    },
                    {
                        data: "sticker",
                    },
                    {
                        data: "licensee",
                    },
                    {
                        data: "allocated_by",
                    },
                    {
                        data: "mobile",
                    },
                    {
                        data: "email",
                    },
                ],
            },
            ml_vessels_datatable_headers: [
                //'Id',
                'Vessel',
                'Rego No',
                'Sticker',
                'Owner',
                'Mobile',
                'Email',
            ],

            ml_vessels_datatable_options: {
                autoWidth: false,
                responsive: true,
                columns: [
                    {
                        data: "vessel_name",
                    },
                    {
                        data: "rego_no",
                    },
                    {
                        data: "sticker_numbers",
                    },
                    {
                        data: "owner",
                    },
                    {
                        data: "mobile",
                    },
                    {
                        data: "email",
                    },
                ],
            },
            ml_authorised_users_datatable_headers: [
                'Number',
                'Vessel',
                'Holder',
                'Mobile',
                'Email',
                'Status',
            ],

            ml_authorised_users_datatable_options: {
                autoWidth: false,
                responsive: true,
                columns: [
                    {
                        data: "lodgement_number",
                    },
                    {
                        data: "vessel_name",
                    },
                    {
                        data: "holder",
                    },
                    {
                        data: "mobile",
                    },
                    {
                        data: "email",
                    },
                    {
                        data: "status",
                    },
                ],
            },

        }
    },
    watch: {
        showExpired: function (value) {
            console.log(value)
            //this.$refs.approvals_datatable.vmDataTable.ajax.reload()
            this.$nextTick(() => {
                this.constructMLAuthorisedUsersTable()
            });
        },
    },
    components: {
        datatable,
        CommsLogs,
        FormSection,
        Applicant,
        OrganisationApplicant,
    },
    computed: {
        debug: function () {
            return this.$route.query.hasOwnProperty('debug') && this.$route.query.debug === 'true' ? true : false
        },
        isLoading: function () {
            return this.loading.length > 0;
        },
        approvalLabel: function () {
            let description = '';
            if (this.approval && this.approval.approval_type_dict) {
                description = this.approval.approval_type_dict.description;
            } else {
                description = "License"
            }
            return description;
        },
        annualAdmissionPermit: function () {
            let permit = false;
            if (this.approval && this.approval.approval_type_dict && this.approval.approval_type_dict.code === 'aap') {
                permit = true;
            }
            return permit;
        },
        authorisedUserPermit: function () {
            let permit = false;
            if (this.approval && this.approval.approval_type_dict && this.approval.approval_type_dict.code === 'aup') {
                permit = true;
            }
            return permit;
        },
        mooringLicence: function () {
            let permit = false;
            if (this.approval && this.approval.approval_type_dict && this.approval.approval_type_dict.code === 'ml') {
                permit = true;
            }
            return permit;
        },
    },
    methods: {
        formatDate: function (data) {
            return data ? moment(data).format(this.DATE_TIME_FORMAT) : '';
        },
        constructMooringsTable: function () {
            let vm = this;
            this.$refs.moorings_datatable.vmDataTable.clear().draw();

            for (let aum of vm.approval.authorised_user_moorings_detail) {
                this.$refs.moorings_datatable.vmDataTable.row.add(
                    {
                        'mooring_name': aum.mooring_name,
                        'sticker': aum.sticker,
                        'licensee': aum.licensee,
                        'allocated_by': aum.allocated_by,
                        'mobile': aum.mobile,
                        'email': aum.email,
                    }
                ).draw();
            }
        },
        constructMLVesselsTable: function () {
            let vm = this;
            this.$refs.ml_vessels_datatable.vmDataTable.clear().draw();

            for (let mlv of vm.approval.mooring_licence_vessels_detail) {
                this.$refs.ml_vessels_datatable.vmDataTable.row.add(
                    {
                        'vessel_name': mlv.vessel_name,
                        'rego_no': mlv.rego_no,
                        'sticker_numbers': mlv.sticker_numbers,
                        'owner': mlv.owner,
                        'mobile': mlv.mobile,
                        'email': mlv.email,
                    }
                ).draw();
            }
        },
        constructMLAuthorisedUsersTable: function () {
            let vm = this;
            this.$refs.ml_authorised_users_datatable.vmDataTable.clear().draw();

            for (let mlau of vm.approval.mooring_licence_authorised_users) {
                if (this.showExpired || (!this.showExpired && ['current'].includes(mlau.status))) {
                    this.$refs.ml_authorised_users_datatable.vmDataTable.row.add(
                        {
                            'lodgement_number': mlau.lodgement_number,
                            'vessel_name': mlau.vessel_name,
                            'holder': mlau.holder,
                            'mobile': mlau.mobile,
                            'email': mlau.email,
                            'status': mlau.status,
                        }
                    ).draw();
                }
            }
        },

        commaToNewline(s) {
            return s.replace(/[,;]/g, '\n');
        },
        viewApprovalPDF: function (id, media_link) {
            let vm = this;
            //console.log(approval);
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.approvals, (id + '/approval_pdf_view_log')), {
            })
                .then((response) => {
                    //console.log(response)
                }, (error) => {
                    console.log(error);
                });
            window.open(media_link, '_blank');
        },
        renewalRevew: function (canBeRenewed) {
            let vm = this;
            Swal.fire({
                title: 'Are you sure?',
                text: 'You are about to ' + (canBeRenewed ? "allow" : "disallow") + ' renewal of approval ' + vm.approval.lodgement_number + '.',
                icon: 'warning',
                reverseButtons: true,
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                confirmButtonText: (canBeRenewed ? 'Allow' : 'Disallow') + ' Renewal'
            }).then((result) => {
                if (result.isConfirmed) {
                    let vm = this;
                    const requestOptions = {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ can_be_renewed: canBeRenewed })
                    };
                    fetch(helpers.add_endpoint_json(api_endpoints.approvals, (vm.approval.id + '/review_renewal')), requestOptions)
                        .then(async response => {
                            const data = await response.json();
                            if (!response.ok) {
                                const error = (data && data.message) || response.statusText;
                                console.log(error)
                                return Promise.reject(error);
                            }
                            let successMessage = 'The approval status has been reset to Current and will expire without being renewed.'
                            if (canBeRenewed) {
                                successMessage = 'The approval holder has been notified that they may renew the approval.';
                            }
                            Swal.fire(
                                'Renewal Review Complete',
                                successMessage,
                                'success'
                            )
                            vm.approval = Object.assign({}, data);
                        }, (error) => {
                            console.log(error);
                        });
                }
            })
        },
        debug_createApprovalPDF: async function () {
            /** Quick and dirty test function to test creating an Approval PDF document
             * from inside the Approval View.
            */

            let vm = this;

            await fetch(helpers.add_endpoint_json(api_endpoints.proposals,
                this.approval.current_proposal + '/test_create_approval_pdf'),
                {
                    body: JSON.stringify(this.approval),
                    method: 'POST',
                    'content-type': 'application/json'
                }).then(async response => {
                    if (!response.ok) {
                        return await response.json().then(json => { throw new Error(json); });
                    } else {
                        return response.json();
                    }
                })
                .then(data => {
                    // Update the linked document in the View
                    vm.approval.licence_document = data.permit;
                })
                .catch(error => {
                    console.log(error);
                });
        }
    },
    created: async function () {
        const response = await fetch(helpers.add_endpoint_json(api_endpoints.approvals, this.$route.params.approval_id))
        const resData = await response.json()
        console.log({ resData })
        this.approval = Object.assign({}, resData);
        this.approval.applicant_id = resData.applicant_id;
        if (this.approval.submitter.postal_address == null) { this.approval.submitter.postal_address = {}; }
        await this.$nextTick(() => {
            if (this.approval && this.approval.id && this.authorisedUserPermit) {
                this.constructMooringsTable();
            }
            if (this.approval && this.approval.id && this.mooringLicence) {
                this.constructMLVesselsTable();
                this.constructMLAuthorisedUsersTable();
            }
        })
    },
}
</script>
