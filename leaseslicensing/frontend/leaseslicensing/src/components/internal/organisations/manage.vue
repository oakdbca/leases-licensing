<template>
    <div id="internalOrgInfo" class="container">
        <div v-if="org" class="row">
            <h3>
                {{ org.ledger_organisation_name }} [ABN: {{ formattedABN }}]
            </h3>
            <div class="col-md-3">
                <CommsLogs
                    :comms_url="comms_url"
                    :logs_url="logs_url"
                    :comms_add_url="comms_add_url"
                    :disable_add_entry="false"
                />
            </div>
            <div class="col-md-9">
                <ul id="pills-tab" class="nav nav-pills" role="tablist">
                    <li class="nav-item">
                        <a
                            id="pills-details-tab"
                            class="nav-link active"
                            data-bs-toggle="pill"
                            href="#pills-details"
                            role="tab"
                            aria-controls="pills-details"
                            aria-selected="true"
                            >Details</a
                        >
                    </li>
                    <li class="nav-item">
                        <a
                            id="pills-other-tab"
                            class="nav-link"
                            data-bs-toggle="pill"
                            href="#pills-other"
                            role="tab"
                            aria-controls="pills-other"
                            aria-selected="false"
                            >Other</a
                        >
                    </li>
                </ul>
                <div class="tab-content">
                    <div
                        id="pills-details"
                        class="tab-pane active"
                        role="tabpanel"
                        aria-labelledby="pills-applications-tab"
                    >
                        <FormSection
                            :form-collapse="false"
                            label="Details"
                            index="details"
                        >
                            <form
                                class="form-horizontal"
                                name="personal_form"
                                method="post"
                            >
                                <div class="row mb-2">
                                    <label
                                        for="ledger_organisation_name"
                                        class="col-sm-3 control-label"
                                        >Name</label
                                    >
                                    <div class="col-sm-9">
                                        <input
                                            v-model="
                                                org.ledger_organisation_name
                                            "
                                            type="text"
                                            class="form-control"
                                            name="ledger_organisation_name"
                                            :readonly="true"
                                        />
                                    </div>
                                </div>
                                <div
                                    v-if="org.ledger_organisation_trading_name"
                                    class="row mb-2"
                                >
                                    <label
                                        for="ledger_organisation_trading_name"
                                        class="col-sm-3 control-label"
                                        >Trading Name</label
                                    >
                                    <div class="col-sm-9">
                                        <input
                                            v-model="
                                                org.ledger_organisation_trading_name
                                            "
                                            type="text"
                                            class="form-control"
                                            name="ledger_organisation_trading_name"
                                            :readonly="true"
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-md-3 control-label"
                                        >ABN</label
                                    >
                                    <div class="col-md-2">
                                        <input
                                            v-model="
                                                org.ledger_organisation_abn
                                            "
                                            type="text"
                                            class="form-control"
                                            name="ledger_organisation_abn"
                                            placeholder=""
                                            :disabled="
                                                !is_leaseslicensing_admin
                                            "
                                            :readonly="true"
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label"
                                        >Email</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="
                                                org.ledger_organisation_email
                                            "
                                            type="text"
                                            class="form-control"
                                            name="ledger_organisation_email"
                                            placeholder=""
                                            :readonly="true"
                                        />
                                    </div>
                                </div>
                            </form>
                        </FormSection>
                        <FormSection
                            v-if="orgHasAddress"
                            :form-collapse="false"
                            label="Address Details"
                            index="addressdetails"
                        >
                            <form
                                class="form-horizontal"
                                action="index.html"
                                method="post"
                            >
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label"
                                        >Street</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="org.address.line1"
                                            type="text"
                                            class="form-control"
                                            name="street"
                                            placeholder=""
                                            :readonly="true"
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label"
                                        >Town/Suburb</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="org.address.locality"
                                            type="text"
                                            class="form-control"
                                            name="surburb"
                                            placeholder=""
                                            :readonly="true"
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label"
                                        >State</label
                                    >
                                    <div class="col-sm-2">
                                        <input
                                            v-model="org.address.state"
                                            type="text"
                                            class="form-control"
                                            name="country"
                                            placeholder=""
                                            :readonly="true"
                                        />
                                    </div>
                                    <label for="" class="col-sm-2 control-label"
                                        >Postcode</label
                                    >
                                    <div class="col-sm-2">
                                        <input
                                            v-model="org.address.postcode"
                                            type="text"
                                            class="form-control"
                                            name="postcode"
                                            placeholder=""
                                            :readonly="true"
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label"
                                        >Country</label
                                    >
                                    <div class="col-sm-4">
                                        <select
                                            v-model="org.address.country"
                                            class="form-control"
                                            name="country"
                                            :readonly="true"
                                        >
                                            <option
                                                v-for="c in countries"
                                                :key="c.alpha2Code"
                                                :value="c.alpha2Code"
                                            >
                                                {{ c.name }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </form>
                        </FormSection>
                        <FormSection
                            :form-collapse="false"
                            label="Contacts"
                            index="contacts"
                        >
                            <TableOrganisationContacts
                                ref="organisation_contacts_datatable"
                                :organisation-id="org.id"
                                level="internal"
                            />
                        </FormSection>
                        <FormSection
                            :form-collapse="false"
                            label="Linked User Accounts"
                            index="linkeduseraccounts"
                        >
                            <form class="form-horizontal">
                                <div class="col-sm-12">
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <p class="fs-6">
                                                Users linked to this
                                                organisation:
                                            </p>
                                        </div>
                                        <div class="mb-3">
                                            <ul
                                                v-if="
                                                    org.delegates &&
                                                    org.delegates.length
                                                "
                                                class="ms-0 ps-0"
                                            >
                                                <span
                                                    v-for="d in org.delegates"
                                                    :key="d.user"
                                                    :class="
                                                        'organisation_admin' ==
                                                        d.user_role
                                                            ? 'bg-primary'
                                                            : 'bg-secondary'
                                                    "
                                                    class="badge me-1 fs-6"
                                                    data-bs-toggle="tooltip"
                                                    data-bs-html="true"
                                                    data-bs-title="<em>Tooltip</em> <u>with</u> <b>HTML</b>"
                                                    @click="
                                                        personRedirect(d.user)
                                                    "
                                                >
                                                    {{ d.full_name }}
                                                    <span
                                                        v-if="
                                                            'organisation_admin' ==
                                                            d.user_role
                                                        "
                                                    >
                                                        (Admin)</span
                                                    >
                                                </span>
                                            </ul>
                                            <div v-else class="col">
                                                <span
                                                    class="badge bg-secondary fs-6"
                                                    >This organisation currently
                                                    has no linked users.</span
                                                >
                                            </div>
                                        </div>
                                        <div class="row">
                                            <BootstrapAlert class="ms-2">
                                                Persons linked to the
                                                organisation are controlled by
                                                the organisation. <br />
                                                The Department cannot manage
                                                this list of people.
                                            </BootstrapAlert>
                                        </div>
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label
                                        for=""
                                        class="col-sm-3 control-label fw-bold"
                                    >
                                        User Pin Code 1:</label
                                    >
                                    <span class="col-sm-3 fw-light">
                                        {{ org.pins.three }}
                                    </span>
                                    <label
                                        for=""
                                        class="col-sm-3 control-label fw-bold"
                                    >
                                        User Pin Code 2:</label
                                    >
                                    <div class="col-sm-3 fw-light">
                                        {{ org.pins.four }}
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label
                                        for=""
                                        class="col-sm-3 control-label fw-bold"
                                    >
                                        Admin Pin Code 1:</label
                                    >
                                    <span class="col-sm-3 fw-light">
                                        {{ org.pins.one }}
                                    </span>
                                    <label
                                        for=""
                                        class="col-sm-3 control-label fw-bold"
                                    >
                                        Admin Pin Code 2:</label
                                    >
                                    <div class="col-sm-3 fw-light">
                                        {{ org.pins.two }}
                                    </div>
                                </div>
                            </form>
                        </FormSection>
                    </div>

                    <div
                        id="pills-other"
                        class="tab-pane"
                        role="tabpanel"
                        aria-labelledby="pills-other-tab"
                    >
                        <FormSection label="Applications" index="applications">
                            <ApplicationsTable
                                ref="proposals_table"
                                level="organisation_view"
                                :target_organisation_id="org.id"
                                :url="proposals_url"
                            />
                        </FormSection>

                        <FormSection label="Approvals" index="approvals">
                            <ApprovalsTable
                                ref="approvals_table"
                                level="organisation_view"
                                :target-organisation-id="org.id"
                                :url="approvals_url"
                            />
                        </FormSection>

                        <FormSection label="Compliances" index="compliances">
                            <CompliancesTable
                                ref="compliances_table"
                                level="organisation_view"
                                :target_organisation_id="org.id"
                                :url="compliances_url"
                            />
                        </FormSection>
                    </div>
                </div>
            </div>
            <AddContact ref="add_contact" :org_id="org.id" />
        </div>
        <div v-else>
            <BootstrapSpinner class="text-primary" :is-loading="true" />
        </div>
    </div>
</template>

<script>
import { api_endpoints, constants, helpers } from '@/utils/hooks';
import ApplicationsTable from '@/components/common/table_proposals';
import ApprovalsTable from '@/components/common/table_approvals.vue';
import CompliancesTable from '@/components/common/table_compliances.vue';
import TableOrganisationContacts from '@/components/common/table_organisation_contacts.vue';
import CommsLogs from '@common-utils/comms_logs.vue';
import AddContact from '@common-utils/add_contact.vue';
import utils from '../utils';
import Swal from 'sweetalert2';
import FormSection from '@/components/forms/section_toggle.vue';

export default {
    name: 'Organisation',
    components: {
        CommsLogs,
        ApplicationsTable,
        ApprovalsTable,
        CompliancesTable,
        AddContact,
        TableOrganisationContacts,
        FormSection,
    },
    data() {
        let vm = this;
        return {
            adBody: 'adBody' + vm._uid,
            aBody: 'aBody' + vm._uid,
            pdBody: 'pdBody' + vm._uid,
            pBody: 'pBody' + vm._uid,
            cdBody: 'cdBody' + vm._uid,
            cBody: 'cBody' + vm._uid,
            oBody: 'oBody' + vm._uid,
            dTab: 'dTab' + vm._uid,
            oTab: 'oTab' + vm._uid,
            org: null,
            loading: [],
            countries: [],
            updatingDetails: false,
            updatingAddress: false,
            updatingContact: false,
            empty_list: '/api/empty_list',
            logsTable: null,
            prev_licence_discount: null,
            prev_application_discount: null,
            is_leaseslicensing_admin: false,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            activate_tables: false,
            comms_url: helpers.add_endpoint_json(
                api_endpoints.organisations,
                vm.$route.params.org_id + '/comms_log'
            ),
            logs_url: helpers.add_endpoint_json(
                api_endpoints.organisations,
                vm.$route.params.org_id + '/action_log'
            ),
            comms_add_url: helpers.add_endpoint_json(
                api_endpoints.organisations,
                vm.$route.params.org_id + '/add_comms_log'
            ),

            contacts_headers: [
                'Name',
                'Phone',
                'Mobile',
                'Fax',
                'Email',
                'Action',
            ],

            //proposals_url: helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/proposals'),
            //approvals_url: api_endpoints.approvals+'?org_id='+vm.$route.params.org_id,
            //compliances_url: api_endpoints.compliances+'?org_id='+vm.$route.params.org_id,

            proposals_url:
                api_endpoints.proposals_paginated_external +
                '&org_id=' +
                vm.$route.params.org_id,
            approvals_url:
                api_endpoints.approvals_paginated_external +
                '&org_id=' +
                vm.$route.params.org_id,
            compliances_url:
                api_endpoints.compliances_paginated_external +
                '&org_id=' +
                vm.$route.params.org_id,

            contacts_options: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                ajax: {
                    url: helpers.add_endpoint_json(
                        api_endpoints.organisations,
                        vm.$route.params.org_id + '/contacts'
                    ),
                    dataSrc: '',
                },
                columns: [
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            return full.first_name + ' ' + full.last_name;
                        },
                    },
                    { data: 'phone_number', defaultContent: '' },
                    { data: 'mobile_number', defaultContent: '' },
                    { data: 'fax_number', defaultContent: '' },
                    { data: 'email', defaultContent: '' },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            if (
                                'Organisation Admin' == full.user_role &&
                                1 == full.admin_count
                            ) {
                                return '';
                            }
                            let links = '';
                            let name = full.first_name + ' ' + full.last_name;
                            links += `<a data-email='${full.email}' data-name='${name}' data-id='${full.id}' class="remove-contact">Remove</a><br/>`;
                            return links;
                        },
                    },
                ],
                processing: true,
            },
        };
    },
    computed: {
        isLoading: function () {
            return this.loading.length == 0;
        },
        formattedABN: function () {
            if (
                this.org.ledger_organisation_abn == null ||
                this.org.ledger_organisation_abn == ''
            ) {
                return '';
            }
            return helpers.formatABN(this.org.ledger_organisation_abn);
        },
        orgHasAddress: function () {
            return (
                this.org &&
                this.org.address &&
                Object.keys(this.org.address).length !== 0
            );
        },
    },
    created: function () {
        let vm = this;
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchOrganisation(vm.$route.params.org_id),
        ];
        Promise.all(initialisers).then((data) => {
            vm.countries = data[0];
            vm.org = data[1];
            vm.org.address = vm.org.address != null ? vm.org.address : {};
            vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
        });
    },
    mounted: function () {
        this.personal_form = document.forms.personal_form;
    },
    methods: {
        handleApplicationCurrencyInput(e) {
            // allow max 2dp
            let vm = this;
            let stringValue = e.target.value.toString();
            let regex = /^\d*(\.\d{1,2})?$/;
            if (!stringValue.match(regex) && vm.org.licence_discount !== '') {
                vm.org.application_discount = vm.prev_application_discount;
            }
            vm.prev_application_discount = vm.org.application_discount;
        },
        handleLicenceCurrencyInput(e) {
            // allow max 2dp
            let vm = this;
            let stringValue = e.target.value.toString();
            let regex = /^\d*(\.\d{1,2})?$/;
            if (!stringValue.match(regex) && vm.org.licence_discount !== '') {
                vm.org.licence_discount = vm.prev_licence_discount;
            }
            vm.prev_licence_discount = vm.org.licence_discount;
        },
        validateApplicationDiscount: function () {
            if (
                this.org.application_discount < 0 ||
                this.org.application_discount > 10000
            ) {
                return false;
            }
            return true;
        },
        validateLicenceDiscount: function () {
            if (
                this.org.licence_discount < 0 ||
                this.org.licence_discount > 10000
            ) {
                return false;
            }
            return true;
        },
        can_update: function () {
            // can update the Organisation section
            if (
                this.validateApplicationDiscount() &&
                this.validateLicenceDiscount()
            ) {
                return true;
            }
            return false;
        },
        personRedirect: function (id) {
            window.location.href = '/internal/person/details/' + id;
        },
        updateDetails: function () {
            let vm = this;
            vm.updatingDetails = true;
            vm.$http
                .post(
                    helpers.add_endpoint_json(
                        api_endpoints.organisations,
                        vm.org.id + '/update_details'
                    ),
                    JSON.stringify(vm.org),
                    {
                        emulateJSON: true,
                    }
                )
                .then(
                    (response) => {
                        vm.updatingDetails = false;
                        vm.org = response.body;
                        if (vm.org.address == null) {
                            vm.org.address = {};
                        }
                        Swal.fire(
                            'Saved',
                            'Organisation details have been saved',
                            'success'
                        );
                    },
                    (error) => {
                        var text = helpers.apiVueResourceError(error);
                        if (typeof text == 'object') {
                            if (
                                Object.prototype.hasOwnProperty.call(
                                    text,
                                    'email'
                                )
                            ) {
                                text = text.email[0];
                            }
                        }
                        Swal.fire(
                            'Error',
                            'Organisation details have cannot be saved because of the following error: ' +
                                text,
                            'error'
                        );
                        vm.updatingDetails = false;
                    }
                );
        },
        updateAddress: function () {
            let vm = this;
            vm.updatingAddress = true;
            vm.$http
                .post(
                    helpers.add_endpoint_json(
                        api_endpoints.organisations,
                        vm.org.id + '/update_address'
                    ),
                    JSON.stringify(vm.org.address),
                    {
                        emulateJSON: true,
                    }
                )
                .then(
                    (response) => {
                        vm.updatingAddress = false;
                        vm.org = response.body;
                        Swal.fire(
                            'Saved',
                            'Address details have been saved',
                            'success'
                        );
                        if (vm.org.address == null) {
                            vm.org.address = {};
                        }
                    },
                    (error) => {
                        console.error(error);
                        vm.updatingAddress = false;
                    }
                );
        },
    },
};
</script>

<style scoped>
.top-buffer-s {
    margin-top: 10px;
}

.actionBtn {
    cursor: pointer;
}

.hidePopover {
    display: none;
}

.discount {
    width: 100px;
}

.row-waiver {
    height: 32px;
}

.badge {
    cursor: pointer;
}
</style>
