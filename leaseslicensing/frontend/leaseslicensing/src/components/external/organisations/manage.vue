<template>
    <div class="container" id="externalOrgInfo">
        <div class="row">
            <div v-if="org" class="col">
                <div class="row">
                    <FormSection :formCollapse="false" label="Organisation Details" index="organisation-details">
                        <form class="form-horizontal" name="personal_form" method="post">

                            <div class="row mb-3">
                                <label for="ledger_organisation_name" class="col-sm-3 control-label">Organisation
                                    Name</label>
                                <div class="col-sm-4">
                                    <input type="text" class="form-control" name="ledger_organisation_name"
                                        v-model="org.ledger_organisation_name">
                                </div>
                            </div>

                            <div class="row mb-3">
                                <label for="trading_name" class="col-sm-3 control-label">Trading
                                    Name</label>
                                <div class="col-sm-4">
                                    <input type="text" class="form-control" name="trading_name" v-model="org.trading_name">
                                </div>
                            </div>

                            <div class="row mb-3">
                                <label for="ledger_organisation_abn" class="col-sm-3 control-label">ABN
                                </label>
                                <div class="col-sm-4">
                                    <input type="text" class="form-control" name="ledger_organisation_abn"
                                        v-model="org.ledger_organisation_abn" disabled>
                                </div>
                            </div>

                            <div class="row mb-3">
                                <label for="ledger_organisation_email" class="col-sm-3 control-label">Email
                                </label>
                                <div class="col-sm-4">
                                    <input type="text" class="form-control" name="ledger_organisation_email"
                                        v-model="org.ledger_organisation_email">
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="col-sm-12">
                                    <button v-if="!updatingDetails" class="float-end btn btn-primary"
                                        @click.prevent="updateDetails()">Update</button>
                                    <button v-else disabled class="float-end btn btn-primary"><i
                                            class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                </div>
                            </div>
                        </form>
                    </FormSection>

                    <FormSection v-if="org" index="address-details" label="Address Details" :formCollapse="false">
                        <form @submit.prevent="" id="address-details" class="mb-2 needs-validation" novalidate>
                            <!-- <div v-if="org"> -->
                                <fieldset class="mb-3">
                                <legend>Postal Address</legend>
                                <div class="address-box">
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="postalAddressLine1" class="form-label">Street</label>
                                        </div>
                                        <div class="col-md-4">
                                            <input type="text" class="form-control" id="postalAddressLine1"
                                                name="postalAddressLine1" v-model="
                                                org.postal_address
                                                .postal_line1
                                                " required />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="postalLocality" class="form-label">Town/Suburb</label>
                                        </div>
                                        <div class="col-md-4">
                                            <input type="text" class="form-control" id="postalLocality"
                                                name="postalLocality" v-model="
                                                org.postal_address
                                                .postal_locality
                                                " required />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="postalState" class="form-label">State</label>
                                        </div>
                                        <div class="col-md-4">
                                            <input type="text" class="form-control" id="postalState"
                                                name="postalState" v-model="
                                                org.postal_address
                                                .postal_state
                                                " required />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="postalPostcode" class="form-label">Postcode</label>
                                        </div>
                                        <div class="col-md-4">
                                            <input type="text" class="form-control" id="postalPostcode"
                                                name="postalPostcode" v-model="
                                                org.postal_address
                                                .postal_postcode
                                                " maxlength="10" required />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="postalPostcode" class="form-label">Country</label>
                                        </div>
                                        <div class="col-md-4">
                                            <select class="form-select" id="country" name="Country" v-model="
                                                org.postal_address
                                                .postal_country
                                                " required>
                                                <option v-for="c in countries" :value="c.code">
                                                    {{ c.name }}
                                                </option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            &nbsp;
                                        </div>
                                        <div class="col-md-6">
                                            <div class="form-check form-switch">
                                                <label for="billingPostcodeSame" class="form-label">
                                                    Billing Address Same as Postal Address</label>
                                                <input @change="toggleBillingAddressFieldsDisabled" class="form-check-input"
                                                    type="checkbox" v-model="org.billing_same_as_postal"
                                                    id="toggleBillingAddressFieldsDisabled">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </fieldset>

                                <fieldset class="mb-3">
                                    <legend>Billing Address</legend>
                                    <div class="address-box">

                                        <div class="row mb-2">
                                            <div class="col-md-2">
                                                <label for="billingAddressLine1" class="form-label">Street</label>
                                            </div>
                                            <div class="col-md-4">
                                                <input type="text" class="form-control billing-address" id="billingAddressLine1"
                                                    name="billingAddressLine1" v-model="
                                                    org.billing_address
                                                    .billing_line1
                                                    " required />
                                            </div>
                                        </div>


                                        <div class="row mb-2">
                                            <div class="col-md-2">
                                                <label for="billingLocality" class="form-label">Town/Suburb</label>
                                            </div>
                                            <div class="col-md-4">
                                                <input type="text" class="form-control billing-address" id="billingLocality"
                                                    name="billingLocality" v-model="
                                                    org.billing_address
                                                    .billing_locality
                                                    " required/>
                                            </div>
                                        </div>

                                        <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="billingState" class="form-label">State</label>
                                        </div>
                                        <div class="col-md-4">
                                            <input type="text" class="form-control billing-address" id="billingState"
                                                name="billingState" v-model="
                                                org.billing_address
                                                .billing_state
                                                " required />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="billingPostcode" class="form-label">Postcode</label>
                                        </div>
                                        <div class="col-md-4">
                                            <input type="text" class="form-control billing-address" id="billingPostcode"
                                                name="billingPostcode" v-model="
                                                org.billing_address
                                                .billing_postcode
                                                " maxlength="10" required />
                                        </div>
                                    </div>
                                    <div class="row mb-4">
                                        <div class="col-md-2">
                                            <label for="billingPostcode" class="form-label">Country</label>
                                        </div>
                                        <div class="col-md-4">
                                            <select class="form-select billing-address" id="country" name="Country" v-model="
                                                org.billing_address
                                                .billing_country
                                                " required>
                                                <option v-for="c in countries" :value="c.code">
                                                    {{ c.name }}
                                                </option>
                                            </select>
                                        </div>
                                    </div>
                                   
                                    </div>
                                </fieldset>
                               
                            <BootstrapLoadingButton text="Update" :isLoading="updatingAddress"
                            @click="validateForm('address-details')" class="btn licensing-btn-primary float-end" />
                            <!-- </div> -->
                        </form>
                    </FormSection>

                    <FormSection :formCollapse="true" label="Contact Details" index="contact-details">
                        <div class="row">
                            <div class="col">
                                <button @click.prevent="addContact()" style="margin-bottom:10px;"
                                    class="btn btn-primary float-end">Add Contact</button>
                            </div>
                        </div>

                        <datatable ref="contacts_datatable" id="organisation_contacts_datatable"
                            :dtOptions="contacts_options" :dtHeaders="contacts_headers" />

                    </FormSection>

                    <FormSection :formCollapse="false" label="Account Pins" index="account-pins">

                        <BootstrapAlert type="warning" icon="exclamation-triangle-fill" class="ms-1">
                            <ul class="list-group">
                                <li class="list-group-item">
                                    You and your organisation are responsible for managing the
                                    distribution of pin codes.
                                </li>
                                <li class="list-group-item">
                                    If you are not sure which pin code to give to a staff member please call
                                    the Tourism and Concessions Branch on (08) 9219 9978.</li>
                                <li class="list-group-item">
                                    Never provide these pin codes to people that are not
                                    authorised
                                    to apply/cancel/surrender/pay fees on behalf of this organisation.</li>
                            </ul>
                        </BootstrapAlert>

                        <h5>Administrator Pins</h5>

                        <BootstrapAlert class="ms-1">
                            <ul class="list-group">
                                <li class="list-group-item">Provide the new user these pin codes if you want the
                                    them to have administrator privileges.</li>
                                <li class="list-group-item">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="input-group mb-2 mt-1">
                                                <span class="input-group-text pin-label" id="basic-addon1">Admin Pin
                                                    1</span>
                                                <input type="text" class="form-control" :value="org.pins.one"
                                                    aria-label="Username" aria-describedby="basic-addon1" readonly>
                                                <span class="input-group-text">copy</span>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="input-group mb-2 mt-1">
                                                <span class="input-group-text pin-label" id="basic-addon1">Admin Pin
                                                    2</span>
                                                <input type="text" class="form-control" :value="org.pins.two"
                                                    aria-label="Username" aria-describedby="basic-addon1" readonly>
                                                <button class="btn-copy input-group-text">copy</button>
                                            </div>
                                        </div>
                                    </div>

                                </li>
                            </ul>
                        </BootstrapAlert>

                        <h5>User Pins</h5>

                        <BootstrapAlert class="ms-1">
                            <ul class="list-group">
                                <li class="list-group-item">Provide the new user these pin codes if you want the
                                    new user to be a regular user.</li>
                                <li class="list-group-item">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="input-group mb-2 mt-1">
                                                <span class="input-group-text pin-label" id="user-pin-1">User Pin 1</span>
                                                <input type="text" class="form-control" :value="org.pins.three"
                                                    aria-label="Username" aria-describedby="user-pin-1" readonly>
                                                <span class="input-group-text">copy</span>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="input-group mb-2 mt-1">
                                                <span class="input-group-text pin-label" id="basic-addon1">User Pin
                                                    2</span>
                                                <input type="text" class="form-control" :value="org.pins.four"
                                                    aria-label="Username" aria-describedby="basic-addon1" readonly>
                                                <span class="input-group-text">copy</span>
                                            </div>
                                        </div>
                                    </div>

                                </li>
                            </ul>
                        </BootstrapAlert>
                    </FormSection>

                    <FormSection :formCollapse="false" label="Linked User Accounts" index="linked-user-accounts">

                        <BootstrapAlert type="warning" icon="exclamation-triangle-fill" class="ms-1">
                            The list of users linked to your organisation is controlled by you and your
                            organisation. The Department cannot manage this list.
                        </BootstrapAlert>

                        <div>
                            <datatable ref="contacts_datatable_user" id="organisation_contacts_datatable_ref"
                                :dtOptions="contacts_options_ref" :dtHeaders="contacts_headers_ref" />
                        </div>
                    </FormSection>

                </div>
                <AddContact ref="add_contact" :org_id="org.id" />
            </div>
            <div v-else>
                <BootstrapSpinner class="text-primary" :isLoading="true" />
            </div>
        </div>
    </div>
</template>

<script>
import Vue from 'vue'
import { api_endpoints, constants, helpers, utils } from '@/utils/hooks'
import datatable from '@vue-utils/datatable.vue'
import AddContact from '@common-utils/add_contact.vue'
import BootstrapLoadingButton from '../../../utils/vue/BootstrapLoadingButton.vue';

export default {
    name: 'Organisation',
    props: {
        org_id: {
            type: Number,
            default: null
        },
        isApplication: {
            type: Boolean,
            default: false
        },
    },
    data() {
        let vm = this;
        return {
            adBody: 'adBody' + vm._uid,
            pBody: 'pBody' + vm._uid,
            cBody: 'cBody' + vm._uid,
            oBody: 'oBody' + vm._uid,
            org: null,
            loading: [],
            countries: [],
            contact_user: {
                first_name: null,
                last_name: null,
                email: null,
                mobile_number: null,
                phone_number: null
            },
            updatingDetails: false,
            updatingAddress: false,
            updatingContact: false,
            logsTable: null,
            myorgperms: null,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            logsDtOptions: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                deferRender: true,
                autowidth: true,
                order: [[2, 'desc']],
                dom:
                    "<'row'<'col-sm-5'l><'col-sm-6'f>>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                processing: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations, vm.$route.params.org_id + '/action_log'),
                    "dataSrc": '',
                },
                columns: [
                    {
                        data: "who",
                    },
                    {
                        data: "what",
                    },
                    {
                        data: "when",
                        mRender: function (data, type, full) {
                            return moment(data).format(vm.DATE_TIME_FORMAT)
                        }
                    },
                ]
            },
            commsDtOptions: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                deferRender: true,
                autowidth: true,
                order: [[0, 'desc']],
                processing: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations, vm.$route.params.org_id + '/comms_log'),
                    "dataSrc": '',
                },
                columns: [
                    {
                        title: 'Date',
                        data: 'created',
                        render: function (date) {
                            return moment(date).format(vm.DATE_TIME_FORMAT);
                        }
                    },
                    {
                        title: 'Type',
                        data: 'type'
                    },
                    {
                        title: 'Reference',
                        data: 'reference'
                    },
                    {
                        title: 'To',
                        data: 'to',
                        render: vm.commaToNewline
                    },
                    {
                        title: 'CC',
                        data: 'cc',
                        render: vm.commaToNewline
                    },
                    {
                        title: 'From',
                        data: 'fromm',
                        render: vm.commaToNewline
                    },
                    {
                        title: 'Subject/Desc.',
                        data: 'subject'
                    },
                    {
                        title: 'Text',
                        data: 'text',
                        'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 100,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-toggle="popover" ' +
                                    'data-trigger="click" ' +
                                    'data-placement="top auto"' +
                                    'data-html="true" ' +
                                    'data-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            return result;
                        },
                        'createdCell': function (cell) {
                            //TODO why this is not working?
                            // the call to popover is done in the 'draw' event
                            $(cell).popover();
                        }
                    },
                    {
                        title: 'Documents',
                        data: 'documents',
                        'render': function (values) {
                            var result = '';
                            _.forEach(values, function (value) {
                                // We expect an array [docName, url]
                                // if it's a string it is the url
                                var docName = '',
                                    url = '';
                                if (_.isArray(value) && value.length > 1) {
                                    docName = value[0];
                                    url = value[1];
                                }
                                if (typeof s === 'string') {
                                    url = value;
                                    // display the first  chars of the filename
                                    docName = _.last(value.split('/'));
                                    docName = _.truncate(docName, {
                                        length: 18,
                                        omission: '...',
                                        separator: ' '
                                    });
                                }
                                result += '<a href="' + url + '" target="_blank"><p>' + docName + '</p></a><br>';
                            });
                            return result;
                        }
                    }
                ]
            },
            commsTable: null,





            contacts_headers: ["Name", "Phone", "Mobile", "Fax", "Email", "Action"],
            contacts_options: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations, vm.$route.params.org_id + '/contacts'),
                    //"url": helpers.add_endpoint_json(api_endpoints.organisations,vm.org_id+'/contacts'),
                    "dataSrc": ''
                },
                columns: [
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            return full.first_name + " " + full.last_name;
                        }
                    },
                    { data: 'phone_number' },
                    { data: 'mobile_number' },
                    { data: 'fax_number' },
                    { data: 'email' },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            let name = full.first_name + ' ' + full.last_name;
                            links += `<a data-email='${full.email}' data-name='${name}' data-id='${full.id}' class="remove-contact">Remove</a><br/>`;
                            return links;
                        }
                    }
                ],
                processing: true
            },

            contacts_headers_ref: ["Name", "Role", "Email", "Status", "Action"],
            contacts_options_ref: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations, vm.$route.params.org_id + '/contacts_exclude'),
                    "dataSrc": ''
                },
                columns: [
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            return full.first_name + " " + full.last_name;
                        }
                    },
                    { data: 'user_role' },
                    { data: 'email' },
                    { data: 'user_status' },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            if (vm.myorgperms.is_admin) {
                                if (full.user_status == 'Pending') {
                                    links += `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="accept_contact">Accept</a><br/>`;
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="decline_contact">Decline</a><br/>`;
                                } else if (full.user_status == 'Suspended') {
                                    links += `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="reinstate_contact">Reinstate</a><br/>`;
                                } else if (full.user_status == 'Active') {
                                    links += `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="unlink_contact">Unlink</a><br/>`;
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="suspend_contact">Suspend</a><br/>`;
                                    if (full.user_role == 'Organisation User') {
                                        links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="make_admin_contact">Make Organisation Admin</a><br/>`;
                                    } else {
                                        links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="make_user_contact">Make Organisation User</a><br/>`;
                                    }
                                } else if (full.user_status == 'Unlinked') {
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="relink_contact">Reinstate</a><br/>`;
                                } else if (full.user_status == 'Declined') {
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="accept_declined_contact">Accept (Previously Declined)</a><br/>`;
                                }
                            }
                            return links;
                        }
                    }
                ],
                processing: true,

            }

        }
    },
    components: {
        datatable,
        AddContact,
        BootstrapLoadingButton
    },
    computed: {
        classCompute: function () {
            return this.isApplication ? 'row' : 'container';
        },
    },
    beforeRouteEnter: function (to, from, next) {
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchOrganisation(to.params.org_id),
            utils.fetchOrganisationPermissions(to.params.org_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.countries = data[0];
                vm.org = Object.assign({}, data[1]);
                vm.myorgperms = data[2];
                vm.org.postal_address = vm.org.postal_address != null ? vm.org.postal_address : {};
                vm.org.billing_address = vm.org.billing_address != null ? vm.org.billing_address : {};
                vm.org.billing_same_as_postal = vm.org.billing_same_as_postal != null ? vm.org.billing_same_as_postal : {};
                if (vm.org.billing_same_as_postal) {
                        vm.toggleBillingAddressFieldsDisabled();
                    }
                // vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
            });
        });
    },
    beforeRouteUpdate: function (to, from, next) {
        let initialisers = [
            utils.fetchOrganisation(to.params.org_id),
            utils.fetchOrganisationPermissions(to.params.org_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.org = Object.assign({}, data[0]);
                vm.myorgperms = data[1];
                vm.org.postal_address = vm.org.postal_address != null ? vm.org.postal_address : {};
                vm.org.billing_address = vm.org.billing_address != null ? vm.org.billing_address : {};
                // vm.org.address = vm.org.address != null ? vm.org.address : {};
                // vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
            });
        });
    },
    methods: {
        addContact: function () {
            this.$refs.add_contact.isModalOpen = true;
        },
        toggleBillingAddressFieldsDisabled: function () {
            console.log('toggleBillingAddressFieldsDisabled')

            $('.billing-address').each(function () {
                if ($(this).attr('disabled')) {
                    $(this).removeAttr('disabled');
                } else {
                    $(this).attr('disabled', 'disabled');
                }
            });
            if (!this.org.billing_same_as_postal) {
                $('.billing-address').first().focus();
                this.org.billing_address = {};
            }
            else{
                this.org.billing_address.billing_line1 = this.org.postal_address.postal_line1;
                this.org.billing_address.billing_locality = this.org.postal_address.postal_locality;
                this.org.billing_address.billing_state = this.org.postal_address.postal_state;
                this.org.billing_address.billing_postcode = this.org.postal_address.postal_postcode;
                this.org.billing_address.billing_country = this.org.postal_address.postal_country;
            }
        },
        eventListeners: function () {
            let vm = this;
            if (typeof vm.$refs.contacts_datatable !== 'undefined') {

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

                vm.$refs.contacts_datatable_user.vmDataTable.on('click', '.accept_contact', (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let id = $(e.target).data('id');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname
                    vm.contact_user.last_name = lastname
                    vm.contact_user.email = email
                    vm.contact_user.mobile_number = mobile
                    vm.contact_user.phone_number = phone
                    swal({
                        title: "Contact Accept",
                        text: "Are you sure you want to accept contact request " + name + " (" + email + ")?",
                        showCancelButton: true,
                        confirmButtonText: 'Accept'
                    }).then((result) => {
                        if (result) {
                            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, vm.org.id + '/accept_user'), JSON.stringify(vm.contact_user), {
                                emulateJSON: true
                            }).then((response) => {
                                swal({
                                    title: 'Contact Accept',
                                    text: 'You have successfully accepted ' + name + '.',
                                    type: 'success',
                                    confirmButtonText: 'OK'
                                }).then(() => {
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }, (error) => {
                                });
                            }, (error) => {
                                swal('Contact Accept', 'There was an error accepting ' + name + '.', 'error')
                            });
                        }
                    }, (error) => {
                    });
                });
                vm.$refs.contacts_datatable_user.vmDataTable.on('click', '.accept_declined_contact', (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let id = $(e.target).data('id');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname
                    vm.contact_user.last_name = lastname
                    vm.contact_user.email = email
                    vm.contact_user.mobile_number = mobile
                    vm.contact_user.phone_number = phone
                    swal({
                        title: "Contact Accept (Previously Declined)",
                        text: "Are you sure you want to accept the previously declined contact request for " + name + " (" + email + ")?",
                        showCancelButton: true,
                        confirmButtonText: 'Accept'
                    }).then((result) => {
                        if (result.value) {
                            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, vm.org.id + '/accept_declined_user'), JSON.stringify(vm.contact_user), {
                                emulateJSON: true
                            }).then((response) => {
                                swal({
                                    title: 'Contact Accept (Previously Declined)',
                                    text: 'You have successfully accepted ' + name + '.',
                                    type: 'success',
                                    confirmButtonText: 'OK'
                                }).then(() => {
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }, (error) => {
                                });
                            }, (error) => {
                                swal('Contact Accept (Previously Declined)', 'There was an error accepting ' + name + '.', 'error')
                            });
                        }
                    }, (error) => {
                    });
                });
                vm.$refs.contacts_datatable_user.vmDataTable.on('click', '.decline_contact', (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let id = $(e.target).data('id');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname
                    vm.contact_user.last_name = lastname
                    vm.contact_user.email = email
                    vm.contact_user.mobile_number = mobile
                    vm.contact_user.phone_number = phone
                    // console.log(vm.contact_user)
                    swal({
                        title: "Contact Decline",
                        text: "Are you sure you want to decline the contact request for " + name + " (" + email + ")?",
                        showCancelButton: true,
                        confirmButtonText: 'Accept'
                    }).then((result) => {
                        if (result) {
                            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, vm.org.id + '/decline_user'), JSON.stringify(vm.contact_user), {
                                emulateJSON: true
                            }).then((response) => {
                                swal({
                                    title: 'Contact Decline',
                                    text: 'You have successfully declined ' + name + '.',
                                    type: 'success',
                                    confirmButtonText: 'OK'
                                }).then(() => {
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }, (error) => {
                                });
                            }, (error) => {
                                swal('Contact Decline', 'There was an error declining ' + name + '.', 'error')
                            });
                        }
                    }, (error) => {
                    });
                });
                vm.$refs.contacts_datatable_user.vmDataTable.on('click', '.unlink_contact', (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let id = $(e.target).data('id');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname
                    vm.contact_user.last_name = lastname
                    vm.contact_user.email = email
                    vm.contact_user.mobile_number = mobile
                    vm.contact_user.phone_number = phone
                    swal({
                        title: "Unlink",
                        text: "Are you sure you want to unlink " + name + " (" + email + ")?",
                        showCancelButton: true,
                        confirmButtonText: 'Accept'
                    }).then((result) => {
                        if (result) {
                            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, vm.org.id + '/unlink_user'), JSON.stringify(vm.contact_user), {
                                emulateJSON: true
                            }).then((response) => {
                                swal({
                                    title: 'Unlink',
                                    text: 'You have successfully unlinked ' + name + '.',
                                    type: 'success',
                                    confirmButtonText: 'OK'
                                }).then(() => {
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }, (error) => {
                                });
                            }, (error) => {
                                if (error.status == 500) {
                                    swal('Unlink', 'Last Organisation Admin can not be unlinked.', 'error');
                                }
                                else {
                                    swal('Unlink', 'There was an error unlinking this user ' + error, 'error');
                                }
                            });
                        }
                    }, (error) => {
                    });
                });
                vm.$refs.contacts_datatable_user.vmDataTable.on('click', '.make_admin_contact', (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let id = $(e.target).data('id');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname
                    vm.contact_user.last_name = lastname
                    vm.contact_user.email = email
                    vm.contact_user.mobile_number = mobile
                    vm.contact_user.phone_number = phone
                    swal({
                        title: "Organisation Admin",
                        text: "Are you sure you want to make " + name + " (" + email + ") an Organisation Admin?",
                        showCancelButton: true,
                        confirmButtonText: 'Accept'
                    }).then((result) => {
                        if (result) {
                            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, vm.org.id + '/make_admin_user'), JSON.stringify(vm.contact_user), {
                                emulateJSON: true
                            }).then((response) => {
                                swal({
                                    title: 'Organisation Admin',
                                    text: 'You have successfully made ' + name + ' an Organisation Admin.',
                                    type: 'success',
                                    confirmButtonText: 'OK'
                                }).then(() => {
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }, (error) => {
                                });
                            }, (error) => {
                                swal('Organisation Admin', 'There was an error making ' + name + ' an Organisation Admin.', 'error')
                            });
                        }
                    }, (error) => {
                    });
                });
                vm.$refs.contacts_datatable_user.vmDataTable.on('click', '.make_user_contact', (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let id = $(e.target).data('id');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname
                    vm.contact_user.last_name = lastname
                    vm.contact_user.email = email
                    vm.contact_user.mobile_number = mobile
                    vm.contact_user.phone_number = phone
                    swal({
                        title: "Organisation User",
                        text: "Are you sure you want to make " + name + " (" + email + ") an Organisation User?",
                        showCancelButton: true,
                        confirmButtonText: 'Accept'
                    }).then((result) => {
                        console.log(result);
                        if (result) {
                            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, vm.org.id + '/make_user'), JSON.stringify(vm.contact_user), {
                                emulateJSON: true
                            }).then((response) => {
                                swal({
                                    title: 'Organisation User',
                                    text: 'You have successfully made ' + name + ' an Organisation User.',
                                    type: 'success',
                                    confirmButtonText: 'OK'
                                }).then(() => {
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }, (error) => {
                                });
                            }, (error) => {
                                console.log(error);
                                var text = helpers.apiVueResourceError(error);
                                swal('Company Admin', 'There was an error making ' + name + ' an Organisation User. ' + text, 'error')
                            });
                        }
                    }, (error) => {
                    });
                });
                vm.$refs.contacts_datatable_user.vmDataTable.on('click', '.suspend_contact', (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let id = $(e.target).data('id');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname
                    vm.contact_user.last_name = lastname
                    vm.contact_user.email = email
                    vm.contact_user.mobile_number = mobile
                    vm.contact_user.phone_number = phone
                    swal({
                        title: "Suspend User",
                        text: "Are you sure you want to Suspend  " + name + " (" + email + ")?",
                        showCancelButton: true,
                        confirmButtonText: 'Accept'
                    }).then((result) => {
                        if (result) {
                            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, vm.org.id + '/suspend_user'), JSON.stringify(vm.contact_user), {
                                emulateJSON: true
                            }).then((response) => {
                                swal({
                                    title: 'Suspend User',
                                    text: 'You have successfully suspended ' + name + ' as a User.',
                                    type: 'success',
                                    confirmButtonText: 'OK'
                                }).then(() => {
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }, (error) => {
                                });
                            }, (error) => {
                                swal('Suspend User', 'There was an error suspending ' + name + ' as a User.', 'error')
                            });
                        }
                    }, (error) => {
                    });
                });
                vm.$refs.contacts_datatable_user.vmDataTable.on('click', '.reinstate_contact', (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let id = $(e.target).data('id');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname
                    vm.contact_user.last_name = lastname
                    vm.contact_user.email = email
                    vm.contact_user.mobile_number = mobile
                    vm.contact_user.phone_number = phone
                    swal({
                        title: "Reinstate User",
                        text: "Are you sure you want to Reinstate  " + name + " (" + email + ")?",
                        showCancelButton: true,
                        confirmButtonText: 'Accept'
                    }).then((result) => {
                        if (result) {
                            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, vm.org.id + '/reinstate_user'), JSON.stringify(vm.contact_user), {
                                emulateJSON: true
                            }).then((response) => {
                                swal({
                                    title: 'Reinstate User',
                                    text: 'You have successfully reinstated ' + name + '.',
                                    type: 'success',
                                    confirmButtonText: 'OK'
                                }).then(() => {
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }, (error) => {
                                });
                            }, (error) => {
                                swal('Reinstate User', 'There was an error reinstating ' + name + '.', 'error')
                            });
                        }
                    }, (error) => {
                    });
                });
                vm.$refs.contacts_datatable_user.vmDataTable.on('click', '.relink_contact', (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let id = $(e.target).data('id');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname
                    vm.contact_user.last_name = lastname
                    vm.contact_user.email = email
                    vm.contact_user.mobile_number = mobile
                    vm.contact_user.phone_number = phone
                    swal({
                        title: "Relink User",
                        text: "Are you sure you want to Relink  " + name + " (" + email + ")?",
                        showCancelButton: true,
                        confirmButtonText: 'Accept'
                    }).then((result) => {
                        if (result) {
                            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, vm.org.id + '/relink_user'), JSON.stringify(vm.contact_user), {
                                emulateJSON: true
                            }).then((response) => {
                                swal({
                                    title: 'Relink User',
                                    text: 'You have successfully relinked ' + name + '.',
                                    type: 'success',
                                    confirmButtonText: 'OK'
                                }).then(() => {
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }, (error) => {
                                });
                            }, (error) => {
                                swal('Relink User', 'There was an error relink ' + name + '.', 'error')
                            });
                        }
                    }, (error) => {
                    });
                });
            } // endif

        },
        updateDetails_noconfirm: function () {
            let vm = this;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, (vm.org.id + '/update_details')), JSON.stringify(vm.org), {
                emulateJSON: true
            })
        },
        validateForm: function (formId) {
            let vm = this;
            var form = document.getElementById(formId)

            if (form.checkValidity()) {
                console.log('Form valid');
                vm.updateAddress();
            } else {
                form.classList.add('was-validated');
                $(form).find("input:invalid").first().focus();
            }

            return false;
        },
        updateDetails: function () {
            let vm = this;
            vm.updatingDetails = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, (vm.org.id + '/update_details')), JSON.stringify(vm.org), {
                emulateJSON: true
            }).then((response) => {
                vm.updatingDetails = false;
                vm.org = response.body;
                if (vm.org.residential_address == null) { vm.org.residential_address = {}; }
                if (vm.org.postal_address == null) { vm.org.postal_address = {}; }
                if (!vm.isApplication) {
                    swal(
                        'Saved',
                        'Organisation details have been saved',
                        'success'
                    )
                }
            }, (error) => {
                console.log('EXTERNAL: ' + JSON.stringify(error));
                var text = helpers.apiVueResourceError(error);
                if (typeof text == 'object') {
                    if (text.hasOwnProperty('email')) {
                        text = text.email[0];
                    }
                }
                swal(
                    'Error',
                    'Organisation details cannot be saved because of the following error: ' + text,
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
            let payload = JSON.stringify({
                'organisation_id':vm.org.id, 
                'organisation_name': vm.org.ledger_organisation_name ? vm.org.ledger_organisation_name:null,
                'organisation_abn':vm.org.ledger_organisation_abn,
                'organisation_email':vm.org.ledger_organisation_email,
                'organisation_trading_name':vm.org.trading_name,
                'postal_address':vm.org.postal_address,
                'billing_address':vm.org.billing_address});
            vm.updatingAddress = true;

            fetch(helpers.add_endpoint_json(api_endpoints.organisations, (vm.org.id + '/update_address')), {
                method: 'POST',
                body:payload,
            })
                .then((response) => {
                vm.updatingAddress = false;
                vm.org = response.body;
                // if (vm.org.postal_address == null) { vm.org.postal_address = {}; }
                // if (vm.org.billing_address == null) { vm.org.billing_address = {}; }
                //console.log("updateAddress: ", vm.org);
                if (!vm.isApplication) {
                    swal(
                        'Saved',
                        'Address details have been saved',
                        'success'
                    )
                }
                // if (vm.org.postal_address == null) { vm.org.postal_address = {}; }
                // if (vm.org.billing_address == null) { vm.org.billing_address = {}; }
                })
                .catch((error) => {
                    console.log(error);
                }).finally(() => {
                    vm.updatingAddress = false;
                });
        },
        unlinkUser: function (d) {
            let vm = this;
            let org = vm.org;
            let org_name = org.name;
            let person = helpers.copyObject(d);
            swal({
                title: "Unlink From Organisation",
                text: "Are you sure you want to unlink " + person.name + " " + person.id + " from " + org.name + " ?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then(() => {
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations, org.id + '/unlink_user'), { 'user': person.id }, {
                    emulateJSON: true
                }).then((response) => {
                    vm.org = response.body;
                    if (vm.org.postal_address == null) { vm.org.postal_address = {}; }
                    if (vm.org.billing_address == null) { vm.org.billing_address = {}; }
                    swal(
                        'Unlink',
                        'You have successfully unlinked ' + person.name + ' from ' + org_name + '.',
                        'success'
                    )
                }, (error) => {
                    swal(
                        'Unlink',
                        'There was an error unlinking ' + person.name + ' from ' + org_name + '. ' + error.body,
                        'error'
                    )
                });
            }, (error) => {
            });
        }
    },
    created: function () {
        let vm = this;
        console.log('vm.$route.params.org_id = ' + vm.$route.params.org_id)
        this.personal_form = document.forms.personal_form;
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchOrganisation(vm.$route.params.org_id),
            utils.fetchOrganisationPermissions(vm.$route.params.org_id)
        ]
        Promise.all(initialisers).then(data => {
            vm.countries = data[0];
            vm.org = Object.assign({}, data[1]);
            vm.myorgperms = data[2];
            vm.org.postal_address = vm.org.postal_address != null ? vm.org.postal_address : {};
            vm.org.billing_address = vm.org.billing_address != null ? vm.org.billing_address : {};
            console.log('vm.org = ' + JSON.stringify(vm.org));
        });
    },
    mounted: function () {
        this.personal_form = document.forms.personal_form;
    },
    updated: function () {
        let vm = this;
        $('.panelClicker[data-toggle="collapse"]').on('click', function () {
            var chev = $(this).children()[0];
            window.setTimeout(function () {
                $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
            }, 100);
        });
        this.$nextTick(() => {
            this.eventListeners();
        });
    }
}
</script>

<style scoped>
.top-buffer-s {
    margin-top: 25px;
}

#organisation_contacts_datatable {
    width: 100% !important;
}

.btn-copy:hover {
    background-color: linear-gradient(rgb(0 0 0/40%) 0 0);
}

.pin-label {
    width: 120px;
}

input[readonly] {
    background-color: white;
}


fieldset,
legend {
    all: revert;
}

legend {
    color: grey;
}

fieldset {
    border-color: #efefef;
    border-style: solid;
}

/* Hide the number input arrows */

/* Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

/* Firefox */
input[type=number] {
    -moz-appearance: textfield;
}
</style>
