<template>
    <div class="container" id="internalOrgInfo">
        <div v-if="org" class="row">
            <h3>{{ org.trading_name }} [ABN: {{ formattedABN }}]</h3>
            <div class="col-md-3">
                <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url"
                    :disable_add_entry="false" />
            </div>
            <div class="col-md-9">
                <ul class="nav nav-pills" id="pills-tab" role="tablist">
                    <li class="nav-item">
                        <a class="nav-link active" id="pills-details-tab" data-bs-toggle="pill" href="#pills-details"
                            role="tab" aria-controls="pills-details" aria-selected="true">Details</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" id="pills-other-tab" data-bs-toggle="pill" href="#pills-other" role="tab"
                            aria-controls="pills-other" aria-selected="false">Other</a>
                    </li>
                </ul>
                <div class="tab-content">
                    <div class="tab-pane active" id="pills-details" role="tabpanel"
                        aria-labelledby="pills-applications-tab">
                        <FormSection :formCollapse="false" label="Details" index="details">
                            <form class="form-horizontal" name="personal_form" method="post">
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label">Trading
                                        Name</label>
                                    <div class="col-sm-9">
                                        <input type="text" class="form-control" name="trading_name" placeholder=""
                                            v-model="org.trading_name">
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-md-3 control-label">ABN</label>
                                    <div class="col-md-7">
                                        <input type="text" class="form-control" name="ledger_organisation_abn"
                                            placeholder="" v-model="org.ledger_organisation_abn"
                                            :disabled="!is_leaseslicensing_admin">
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label">Email</label>
                                    <div class="col-sm-6">
                                        <input type="text" class="form-control" name="ledger_organisation_email"
                                            placeholder="" v-model="org.ledger_organisation_email">
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label fw-bold">Waivers</label>
                                </div>
                                <div class="row row-waiver mb-3">
                                    <div class="col-sm-4">
                                        <label class="control-label float-end" for="Name">
                                            T Class application fee
                                        </label>
                                    </div>
                                    <div class="col-sm-1">
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox" :value="true"
                                                v-model="org.apply_application_discount" ref="application_discount_yes" />
                                        </div>
                                    </div>
                                    <div class="col-sm-7">
                                        <div class="row" v-show="org.apply_application_discount">
                                            <div class="col-auto">
                                                <div class="input-group input-group-sm">
                                                    <span class="input-group-text" id="dollars-addon">$</span>
                                                    <input type="number" class="form-control discount" min="0"
                                                        name="application_discount"
                                                        v-model.number="org.application_discount"
                                                        @input="handleApplicationCurrencyInput"
                                                        aria-label="application_discount" aria-describedby="dollars-addon">
                                                </div>
                                            </div>
                                            <div v-show="!validateLicenceDiscount()" class="col-auto">
                                                <div class="text-danger form-text">Must be
                                                    between
                                                    $0 - $10,000 </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="row row-waiver mb-3">
                                    <div class="col-sm-4">
                                        <label class="control-label float-end" for="Name">T Class licence
                                            fee</label>
                                    </div>
                                    <div class="col-sm-1">
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox"
                                                v-model="org.apply_licence_discount" ref="licence_discount_yes" />
                                        </div>
                                    </div>
                                    <div class="col-sm-7">
                                        <div class="row" v-show="org.apply_licence_discount">
                                            <div class="col-auto">
                                                <div class="input-group input-group-sm mb-0">
                                                    <span class="input-group-text" id="dollars-addon">$</span>
                                                    <input type="number" class="form-control discount" min="0"
                                                        name="licence_discount" v-model.number="org.licence_discount"
                                                        @input="handleLicenceCurrencyInput" aria-label="licence_discount"
                                                        aria-describedby="dollars-addon">
                                                </div>
                                            </div>
                                            <div v-show="!validateLicenceDiscount()" class="col-auto">
                                                <div class="text-danger form-text">Must be
                                                    between
                                                    $0 - $10,000 </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <div class="col-sm-12">
                                        <button v-if="!updatingDetails" class="float-end btn btn-primary"
                                            @click.prevent="updateDetails()" :disabled="!can_update()">Update</button>
                                        <button v-else disabled class="float-end btn btn-primary"><i
                                                class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                    </div>
                                </div>
                            </form>
                        </FormSection>
                        <FormSection v-if="orgHasAddress" :formCollapse="true" label="Address Details"
                            index="addressdetails">
                            <form class="form-horizontal" action="index.html" method="post">
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label">Street</label>
                                    <div class="col-sm-6">
                                        <input type="text" class="form-control" name="street" placeholder=""
                                            v-model="org.address.line1">
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label">Town/Suburb</label>
                                    <div class="col-sm-6">
                                        <input type="text" class="form-control" name="surburb" placeholder=""
                                            v-model="org.address.locality">
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label">State</label>
                                    <div class="col-sm-2">
                                        <input type="text" class="form-control" name="country" placeholder=""
                                            v-model="org.address.state">
                                    </div>
                                    <label for="" class="col-sm-2 control-label">Postcode</label>
                                    <div class="col-sm-2">
                                        <input type="text" class="form-control" name="postcode" placeholder=""
                                            v-model="org.address.postcode">
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label">Country</label>
                                    <div class="col-sm-4">
                                        <select class="form-control" name="country" v-model="org.address.country">
                                            <option v-for="c in countries" :value="c.alpha2Code">{{
                                                c.name }}</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <div class="col-sm-12">
                                        <button v-if="!updatingAddress" class="float-end btn btn-primary"
                                            @click.prevent="updateAddress()">Update</button>
                                        <button v-else disabled class="float-end btn btn-primary"><i
                                                class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                    </div>
                                </div>
                            </form>
                        </FormSection>
                        <FormSection :formCollapse="true" label="Contacts" index="contacts">
                            <div class="row">
                                <div class="col">
                                    <button @click.prevent="addContact()" style="margin-bottom:10px;"
                                        class="btn btn-primary float-end">Add Contact</button>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <datatable @vue:mounted="addOrgContactEventListeners" ref="contacts_datatable"
                                        id="organisation_contacts_datatable" :dtOptions="contacts_options"
                                        :dtHeaders="contacts_headers" />
                                </div>
                            </div>
                        </FormSection>
                        <FormSection :formCollapse="true" label="Linked User Accounts" index="linkeduseraccounts">
                            <form class="form-horizontal">
                                <div class="col-sm-12">
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <p class="fs-6">Users linked to this organisation:</p>
                                        </div>
                                        <div class="mb-3">
                                            <ul v-if="org.delegates && org.delegates.length" class="ms-0 ps-0">
                                                <span @click="personRedirect(d.user)" v-for="d in org.delegates"
                                                    :class="'organisation_admin' == d.user_role ? 'bg-primary' : 'bg-secondary'"
                                                    class="badge me-1 fs-6" data-bs-toggle="tooltip" data-bs-html="true"
                                                    data-bs-title="<em>Tooltip</em> <u>with</u> <b>HTML</b>">
                                                    {{ d.full_name }}
                                                    <span v-if="'organisation_admin' == d.user_role">
                                                        (Admin)</span>
                                                </span>

                                            </ul>
                                            <div v-else class="col">
                                                <span class="badge bg-secondary fs-6">This organisation currently
                                                    has no
                                                    linked
                                                    users.</span>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <BootstrapAlert class="ms-2">
                                                Persons linked to the organisation are controlled by
                                                the organisation. <br />
                                                The Department cannot manage this
                                                list of people.
                                            </BootstrapAlert>
                                        </div>
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label fw-bold">
                                        User Pin Code 1:</label>
                                    <span class="col-sm-3 fw-light">
                                        {{ org.pins.three }}
                                    </span>
                                    <label for="" class="col-sm-3 control-label fw-bold">
                                        User Pin Code 2:</label>
                                    <div class="col-sm-3 fw-light">
                                        {{ org.pins.four }}
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-sm-3 control-label fw-bold">
                                        Admin Pin Code 1:</label>
                                    <span class="col-sm-3 fw-light">
                                        {{ org.pins.one }}
                                    </span>
                                    <label for="" class="col-sm-3 control-label fw-bold">
                                        Admin Pin Code 2:</label>
                                    <div class="col-sm-3 fw-light">
                                        {{ org.pins.two }}
                                    </div>
                                </div>
                            </form>

                        </FormSection>
                    </div>

                    <div class="tab-pane" id="pills-other" role="tabpanel" aria-labelledby="pills-other-tab">
                        <FormSection label="Applications" index="applications">
                            <ApplicationsTable ref="proposals_table" level="organisation_view"
                                :target_organisation_id="org.id" :url='proposals_url' />
                        </FormSection>

                        <FormSection label="Approvals" index="approvals">
                            <ApprovalsTable ref="approvals_table" level="organisation_view" :target_organisation_id="org.id"
                                :url='approvals_url' />
                        </FormSection>

                        <FormSection label="Compliances" index="compliances">
                            <CompliancesTable ref="compliances_table" level='organisation_view'
                                :target_organisation_id="org.id" :url='compliances_url' />
                        </FormSection>
                    </div>
                </div>
            </div>
            <AddContact ref="add_contact" :org_id="org.id" />
        </div>
        <div v-else>
            <BootstrapSpinner class="text-primary" :isLoading="true" />
        </div>
    </div>
</template>

<script>

import { api_endpoints, constants, helpers } from '@/utils/hooks'
import datatable from '@vue-utils/datatable.vue'
import ApplicationsTable from "@/components/common/table_proposals"
import ApprovalsTable from '@/components/common/table_approvals.vue'
import CompliancesTable from '@/components/common/table_compliances.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import AddContact from '@common-utils/add_contact.vue'
import utils from '../utils'
import Swal from 'sweetalert2'


export default {
    name: 'Organisation',
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
            comms_url: helpers.add_endpoint_json(api_endpoints.organisations, vm.$route.params.org_id + '/comms_log'),
            logs_url: helpers.add_endpoint_json(api_endpoints.organisations, vm.$route.params.org_id + '/action_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.organisations, vm.$route.params.org_id + '/add_comms_log'),

            contacts_headers: ["Name", "Phone", "Mobile", "Fax", "Email", "Action"],

            //proposals_url: helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/proposals'),
            //approvals_url: api_endpoints.approvals+'?org_id='+vm.$route.params.org_id,
            //compliances_url: api_endpoints.compliances+'?org_id='+vm.$route.params.org_id,

            proposals_url: api_endpoints.proposals_paginated_external + '&org_id=' + vm.$route.params.org_id,
            approvals_url: api_endpoints.approvals_paginated_external + '&org_id=' + vm.$route.params.org_id,
            compliances_url: api_endpoints.compliances_paginated_external + '&org_id=' + vm.$route.params.org_id,

            contacts_options: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations, vm.$route.params.org_id + '/contacts'),
                    "dataSrc": ''
                },
                columns: [
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            return full.first_name + " " + full.last_name;
                        }
                    },
                    { data: 'phone_number', "defaultContent": "" },
                    { data: 'mobile_number', "defaultContent": "" },
                    { data: 'fax_number', "defaultContent": "" },
                    { data: 'email', "defaultContent": "" },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            if ('Organisation Admin' == full.user_role && 1 == full.admin_count) {
                                return '';
                            }
                            let links = '';
                            let name = full.first_name + ' ' + full.last_name;
                            links += `<a data-email='${full.email}' data-name='${name}' data-id='${full.id}' class="remove-contact">Remove</a><br/>`;
                            return links;
                        }
                    },
                ],
                processing: true
            }
        }
    },
    components: {
        datatable,
        CommsLogs,
        ApplicationsTable,
        ApprovalsTable,
        CompliancesTable,
        AddContact,
    },
    computed: {
        isLoading: function () {
            return this.loading.length == 0;
        },
        formattedABN: function () {
            if (this.org.ledger_organisation_abn == null || this.org.ledger_organisation_abn == '') {
                return ''
            }
            return helpers.formatABN(this.org.ledger_organisation_abn)
        },
        orgHasAddress: function () {
            return this.org && this.org.address && Object.keys(this.org.address).length !== 0
        }
    },
    methods: {
        handleApplicationCurrencyInput(e) {
            // allow max 2dp
            let vm = this;
            let stringValue = e.target.value.toString()
            let regex = /^\d*(\.\d{1,2})?$/
            if (!stringValue.match(regex) && vm.org.licence_discount !== '') {
                vm.org.application_discount = vm.prev_application_discount
            }
            vm.prev_application_discount = vm.org.application_discount
        },
        handleLicenceCurrencyInput(e) {
            // allow max 2dp
            let vm = this;
            let stringValue = e.target.value.toString()
            let regex = /^\d*(\.\d{1,2})?$/
            if (!stringValue.match(regex) && vm.org.licence_discount !== '') {
                vm.org.licence_discount = vm.prev_licence_discount
            }
            vm.prev_licence_discount = vm.org.licence_discount
        },
        validateApplicationDiscount: function () {
            if (this.org.application_discount < 0 || this.org.application_discount > 10000) {
                return false;
            }
            return true;
        },
        validateLicenceDiscount: function () {
            if (this.org.licence_discount < 0 || this.org.licence_discount > 10000) {
                return false;
            }
            return true;
        },
        can_update: function () {
            // can update the Organisation section
            if (this.validateApplicationDiscount() && this.validateLicenceDiscount()) {
                return true;
            }
            return false;
        },
        addContact: function () {
            this.$refs.add_contact.isModalOpen = true;
            this.$nextTick(() => {
                this.$refs.add_contact.$refs.first_name.focus();
            });
        },
        personRedirect: function (id) {
            window.location.href = '/internal/person/details/' + id;
        },
        addOrgContactEventListeners: function () {
            let vm = this;
            vm.$refs.contacts_datatable.vmDataTable.on('click', '.remove-contact', (e) => {
                e.preventDefault();

                let name = $(e.target).data('name');
                let email = $(e.target).data('email');
                let id = $(e.target).data('id');
                Swal.fire({
                    title: "Delete Contact",
                    text: `Are you sure you want to remove ${name} (${email}) as a contact  ?`,
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonText: 'Accept'
                }).then((result) => {
                    if (result.isConfirmed) {
                        vm.deleteContact(id);
                    }
                }, (error) => {
                    console.log(error);
                });
            });
            // Fix the table responsiveness when tab is shown
            $('a[href="#' + vm.oTab + '"]').on('shown.bs.tab', function (e) {
                vm.$refs.proposals_table.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
                vm.$refs.approvals_table.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
                vm.$refs.compliances_table.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
            });
        },
        updateDetails: function () {
            let vm = this;
            vm.updatingDetails = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, (vm.org.id + '/update_details')), JSON.stringify(vm.org), {
                emulateJSON: true
            }).then((response) => {
                vm.updatingDetails = false;
                vm.org = response.body;
                if (vm.org.address == null) { vm.org.address = {}; }
                Swal.fire(
                    'Saved',
                    'Organisation details have been saved',
                    'success'
                )
            }, (error) => {
                console.log('INTERNAL: ' + error);
                var text = helpers.apiVueResourceError(error);
                if (typeof text == 'object') {
                    if (text.hasOwnProperty('email')) {
                        text = text.email[0];
                    }
                }
                Swal.fire(
                    'Error',
                    'Organisation details have cannot be saved because of the following error: ' + text,
                    'error'
                )
                vm.updatingDetails = false;
            });
        },
        addedContact: function () {
            let vm = this;
            Swal.fire(
                'Added',
                'The contact has been successfully added.',
                'success'
            )
            vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
        },
        deleteContact: function (id) {
            let vm = this;
            const requestOptions = {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
            };
            fetch(helpers.add_endpoint_json(api_endpoints.organisation_contacts, id), requestOptions)
                .then(async response => {
                    if (204 === response.status) {
                        Swal.fire(
                            'Contact Deleted',
                            'The contact was successfully deleted',
                            'success'
                        )
                        vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
                    }
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        if (400 == response.status) {
                            const errorString = helpers.getErrorStringFromResponseData(data);
                            Swal.fire({
                                title: 'Unable to Delete Contact',
                                html: `${errorString}`,
                                icon: 'error'
                            })
                        }
                        console.log(data)
                        return Promise.reject(error);
                    }
                    Swal.fire(
                        'Contact Deleted',
                        'The contact was successfully deleted',
                        'success'
                    )
                    vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
                })
                .catch(error => {
                    console.error("There was an error!", error);
                });

        },
        updateAddress: function () {
            let vm = this;
            vm.updatingAddress = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, (vm.org.id + '/update_address')), JSON.stringify(vm.org.address), {
                emulateJSON: true
            }).then((response) => {
                vm.updatingAddress = false;
                vm.org = response.body;
                Swal.fire(
                    'Saved',
                    'Address details have been saved',
                    'success'
                )
                if (vm.org.address == null) { vm.org.address = {}; }
            }, (error) => {
                console.log(error);
                vm.updatingAddress = false;
            });
        },
    },
    created: function () {
        console.log('created')
        let vm = this;
        console.log('vm.$route.params = ', vm.$route.params);
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchOrganisation(vm.$route.params.org_id),
        ]
        Promise.all(initialisers).then(data => {
            console.log('vm.org: ', vm.org)
            vm.countries = data[0];
            vm.org = data[1];
            vm.org.address = vm.org.address != null ? vm.org.address : {};
            vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
        });
    },
    mounted: function () {
        let vm = this;
        this.personal_form = document.forms.personal_form;
    },
}
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
