<template>
    <div class="container" id="internalOrgInfo">
        <div class="row">
            <div v-if="org" class="col-md-10 col-md-offset-1">
                <div class="row">
                    <h3>{{ org.trading_name }} [ABN: {{ formattedABN }}]</h3>
                    <div class="col-md-3">
                        <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url"
                            :disable_add_entry="false" />
                    </div>
                    <div class="col-md-9">
                        <ul class="nav nav-pills" id="pills-tab" role="tablist">
                            <li class="nav-item">
                                <a class="nav-link active" id="pills-details-tab" data-bs-toggle="pill"
                                    href="#pills-details" role="tab" aria-controls="pills-details"
                                    aria-selected="true">Details</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" id="pills-other-tab" data-bs-toggle="pill" href="#pills-other"
                                    role="tab" aria-controls="pills-other" aria-selected="false">Other</a>
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
                                                <input type="text" class="form-control" name="last_name" placeholder=""
                                                    v-model="org.organisation_abn" :disabled="!is_leaseslicensing_admin">
                                            </div>
                                        </div>
                                        <div class="row mb-2">
                                            <label for="" class="col-sm-3 control-label">Email</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="last_name" placeholder=""
                                                    v-model="org.email">
                                            </div>
                                        </div>
                                        <div class="row mb-2">
                                            <div class="row">
                                                <div class="col-sm-5">
                                                    <label class="control-label pull-right" for="Name">
                                                        Apply waiver for T Class application fee
                                                    </label>
                                                </div>
                                                <div class="col-sm-2">
                                                    <div class="form-check form-switch">
                                                        <input class="form-check-input" type="checkbox" :value="true"
                                                            v-model="org.apply_application_discount"
                                                            ref="application_discount_yes" /> Yes
                                                    </div>
                                                </div>
                                                <div class="col-sm-5">
                                                    <div v-show="org.apply_application_discount">
                                                        <div class="col-sm-3">
                                                            <label class="control-label pull-left" for="Name">Waiver</label>
                                                        </div>
                                                        <div class="col-sm-6 input-group">
                                                            <label class="input-group-addon" for="number">$</label>
                                                            <input type="number" class="form-control" min="0"
                                                                name="application_discount"
                                                                v-model.number="org.application_discount"
                                                                @input="handleApplicationCurrencyInput">
                                                        </div>
                                                        <div v-show="!validateApplicationDiscount()">
                                                            <p style="color:red;"> Waiver amount must be
                                                                between
                                                                $0 - $10,000 </p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row mb-2">
                                            <div class="row">
                                                <div class="col-sm-5">
                                                    <label class="control-label pull-right" for="Name">Apply
                                                        waiver for T Class licence fee</label>
                                                </div>
                                                <div class="col-sm-1">
                                                    <label>
                                                        <input type="radio" :value="true"
                                                            v-model="org.apply_licence_discount"
                                                            ref="licence_discount_yes" />Yes
                                                    </label>
                                                </div>
                                                <div class="col-sm-1">
                                                    <label>
                                                        <input type="radio" :value="false"
                                                            v-model="org.apply_licence_discount" />No
                                                    </label>
                                                </div>
                                                <div class="col-sm-4">
                                                    <div v-show="org.apply_licence_discount">
                                                        <div class="col-sm-3">
                                                            <label class="control-label pull-left" for="Name">Waiver</label>
                                                        </div>
                                                        <div class="col-sm-6 input-group">
                                                            <label class="input-group-addon" for="number">$</label>
                                                            <input type="number" class="form-control" min="0"
                                                                name="licence_discount"
                                                                v-model.number="org.licence_discount"
                                                                @input="handleLicenceCurrencyInput">
                                                        </div>
                                                        <div v-show="!validateLicenceDiscount()">
                                                            <p style="color:red;"> Waiver amount must be
                                                                between
                                                                $0 - $10,000 </p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row mb-2">
                                            <div class="col-sm-12">
                                                <button v-if="!updatingDetails" class="pull-right btn btn-primary"
                                                    @click.prevent="updateDetails()"
                                                    :disabled="!can_update()">Update</button>
                                                <button v-else disabled class="pull-right btn btn-primary"><i
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
                                                <button v-if="!updatingAddress" class="pull-right btn btn-primary"
                                                    @click.prevent="updateAddress()">Update</button>
                                                <button v-else disabled class="pull-right btn btn-primary"><i
                                                        class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                            </div>
                                        </div>
                                    </form>
                                </FormSection>
                                <FormSection :formCollapse="true" label="Contacts" index="contacts">
                                    <form class="form-horizontal" action="index.html" method="post">
                                        <div class="col-sm-12">
                                            <button @click.prevent="addContact()" style="margin-bottom:10px;"
                                                class="btn btn-primary pull-right">Add Contact</button>
                                        </div>
                                        <datatable @hook:mounted="addOrgContactEventListeners" ref="contacts_datatable"
                                            id="organisation_contacts_datatable" :dtOptions="contacts_options"
                                            :dtHeaders="contacts_headers" />
                                    </form>
                                </FormSection>
                                <FormSection :formCollapse="true" label="Linked User Accounts" index="linkeduseraccounts">
                                    <form class="form-horizontal">
                                        <div class="col-sm-12">
                                            <div class="row">
                                                <div class="col-sm-12">
                                                    <p class="fs-6">Users linked to this organisation:</p>
                                                </div>
                                                <div class="mb-3">
                                                    <ul v-if="org.delegate_email_users && org.delegate_email_users.length"
                                                        class="ms-0 ps-0">
                                                        <span @click="personRedirect(d.id)"
                                                            v-for="d in org.delegate_email_users"
                                                            class="badge bg-secondary me-1 fs-6" data-bs-toggle="tooltip"
                                                            data-bs-html="true"
                                                            data-bs-title="<em>Tooltip</em> <u>with</u> <b>HTML</b>">
                                                            {{ d.first_name }}
                                                            {{ d.last_name }}
                                                        </span>

                                                    </ul>
                                                    <div v-else class="col">
                                                        <span class="badge bg-secondary">This organisation currently has no
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
                                    <ApprovalsTable ref="approvals_table" level="organisation_view"
                                        :target_organisation_id="org.id" :url='approvals_url' />
                                </FormSection>

                                <FormSection label="Compliances" index="compliances">
                                    <CompliancesTable ref="compliances_table" level='organisation_view'
                                        :target_organisation_id="org.id" :url='compliances_url' />
                                </FormSection>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else>
                <BootstrapSpinner class="text-primary" :isLoading="true" />
            </div>
        </div>
    </div>
    <!--AddContact ref="add_contact" :org_id="org.id" /-->
</template>

<script>
import { api_endpoints, constants, helpers } from '@/utils/hooks'
import datatable from '@vue-utils/datatable.vue'
// import AddContact from '@common-utils/add_contact.vue'
import ApplicationsTable from "@/components/common/table_proposals"
import ApprovalsTable from '@/components/common/table_approvals.vue'
import CompliancesTable from '@/components/common/table_compliances.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import utils from '../utils'
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
            profile: {},
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
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations, vm.$route.params.org_id + '/contacts'),
                    "dataSrc": ''
                },
                columns: [
                    {
                        mRender: function (data, type, full) {
                            return full.first_name + " " + full.last_name;
                        }
                    },
                    { data: 'phone_number' },
                    { data: 'mobile_number' },
                    { data: 'fax_number' },
                    { data: 'email' },
                    {
                        mRender: function (data, type, full) {
                            let links = '';
                            let name = full.first_name + ' ' + full.last_name;
                            links += `<a data-email='${full.email}' data-name='${name}' data-id='${full.id}' class="remove-contact">Remove</a><br/>`;
                            return links;
                        }
                    }
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
        // AddContact,
    },
    computed: {
        isLoading: function () {
            return this.loading.length == 0;
        },
        formattedABN: function () {
            if (this.org.organisation_abn == null || this.org.organisation_abn == '') {
                return ''
            }
            return helpers.formatABN(this.org.organisation_abn)
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
                swal({
                    title: "Delete Contact",
                    text: "Are you sure you want to remove " + name + "(" + email + ") as a contact  ?",
                    type: "error",
                    showCancelButton: true,
                    confirmButtonText: 'Accept'
                }).then(() => {
                    vm.deleteContact(id);
                }, (error) => {
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
                swal(
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
                swal(
                    'Error',
                    'Organisation details have cannot be saved because of the following error: ' + text,
                    'error'
                )
                vm.updatingDetails = false;
            });
        },
        addedContact: function () {
            let vm = this;
            swal(
                'Added',
                'The contact has been successfully added.',
                'success'
            )
            vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
        },
        deleteContact: function (id) {
            let vm = this;

            vm.$http.delete(helpers.add_endpoint_json(api_endpoints.organisation_contacts, id), {
                emulateJSON: true
            }).then((response) => {
                swal(
                    'Contact Deleted',
                    'The contact was successfully deleted',
                    'success'
                )
                vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
            }, (error) => {
                console.log(error);
                swal(
                    'Contact Deleted',
                    'The contact could not be deleted because of the following error ' + error,
                    'error'
                )
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
                swal(
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
            utils.fetchProfile()
        ]
        Promise.all(initialisers).then(data => {
            console.log('vm.org: ', vm.org)
            vm.countries = data[0];
            vm.org = data[1];
            vm.profile = data[2];
            vm.org.address = vm.org.address != null ? vm.org.address : {};
            vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
            vm.is_leaseslicensing_admin = vm.profile.is_leaseslicensing_admin;
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

.input-group {
    display: table;
    white-space: nowrap;
    vertical-align: top;
    width: 75%;
}

.input-group .form-control {
    display: table-cell;
    vertical-align: top;
    width: 75%;
}

.input-group .input-group-addon {
    display: table-cell;
    width: 1%;
    vertical-align: top;
    background: #2f353e;
    color: #fff;
    font-size: 1.15rem;
    line-height: 19px;
    padding-left: 10px;
    padding-right: 10px;
}

.badge {
    cursor: pointer;
}
</style>
